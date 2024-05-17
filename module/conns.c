#include "fw.h"
#include <stdbool.h>
#include <linux/list.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/device.h>

struct mitm_input
{
    __be32 clip;
    __be16 clport;
    __be32 svip;
    __be16 svport;
    __be16 mitmport;
} __attribute__((packed));

__u32 conncount = 0;
static LIST_HEAD(connlist);

__be16 ftpports[MAX_CONNS];
size_t ftpcount = 0;

ssize_t conns_show(struct device *dev, struct device_attribute *attr, char *buf)
{
    conn_entry *iter;
    __u32 i = 0;

    *((__u32 *)buf) = conncount; // Write number of connections
    list_for_each_entry(iter, &connlist, list)
    {
        if (i >= MAX_CONNS)
            break;
        memcpy(buf + 4 + sizeof(conn_entry) * i, iter, sizeof(conn_entry));
        ++i;
    }

    return i * sizeof(conn_entry) + 4;
}

unsigned int conn_filter(struct iphdr *iphead, struct tcphdr *tcphead)
{
    conn_entry *iter, *entry;
    bool found = false;
    bool svsend = false;
    
    list_for_each_entry(iter, &connlist, list)
    {
        if (iter->cl_ip == iphead->saddr && iter->cl_port == tcphead->source && iter->sv_ip == iphead->daddr && iter->sv_port == tcphead->dest)
        {
            found = true;
            entry = iter;
            break;
        }
        else if (iter->sv_ip == iphead->saddr && iter->sv_port == tcphead->source && iter->cl_ip == iphead->daddr && iter->cl_port == tcphead->dest)
        {
            found = true;
            svsend = true;
            entry = iter;
            break;
        }
    }
    if (!found)
    {
        // No matching open connection
        // printk("TCP packet %pI4:%u -> %pI4:%u without matching connection\n", &iphead->saddr, htons(tcphead->source)
        //     ,&iphead->daddr, htons(tcphead->dest));
        return NF_DROP;
    }
    // We have a relevant connection
    if (svsend) // Server -> Client
    {
        switch (entry->connstate)
        {
        case HANDSHAKE_SYN_SENT:
            if (tcphead->syn && !tcphead->fin)
            { // ACK is implied
                // printk("Server->Client SYN/ACK\n");
                entry->connstate = HANDSHAKE_SYNACK_SENT;
                return NF_ACCEPT;
            }
            else if (tcphead->rst)
            {
                // printk("Server reset connection\n");
                list_del(&entry->list);
                kfree(entry);
                conncount--;
                return NF_ACCEPT;
            }
            return NF_DROP;
        case ESTABLISHED:
            if (!tcphead->syn && tcphead->fin)
            {
                entry->connstate = CLIENT_SENT_FIN;
                // Swap client/server roles for disconnection purposes
                __be32 tempIP = entry->cl_ip;
                __be16 tempPort = entry->cl_port;
                entry->cl_ip = entry->sv_ip;
                entry->cl_port = entry->sv_port;
                entry->sv_ip = tempIP;
                entry->sv_port = tempPort;
                // printk("Original server started disconnect\n");
            }
            // printk("Server->client conn packet\n");
            return NF_ACCEPT;
        case CLIENT_SENT_FIN:
            if (!tcphead->syn && !tcphead->fin)
            {
                entry->connstate = SERVER_ACKNOWLEDGED_FIN;
                // printk("First FIN acknowledged\n");
                return NF_ACCEPT;
            }
            return NF_DROP;
        case SERVER_ACKNOWLEDGED_FIN:
            if (!tcphead->syn && tcphead->fin)
            {
                // printk("Other side sent FIN\n");
                entry->connstate = SERVER_ACCEPTED_FIN;
                return NF_ACCEPT;
            }
            return NF_DROP;
        default:
            // printk("S->C default dropped %pI4:%u -> %pI4:%u state %d SYN: %d FIN: %d RST: %d\n", &iphead->saddr, htons(tcphead->source)
            //     ,&iphead->daddr, htons(tcphead->dest), entry->connstate, tcphead->syn, tcphead->fin, tcphead->rst);
            return NF_DROP;
        }
    }
    else // Client -> Server
    {
        switch (entry->connstate)
        {
        case HANDSHAKE_SYNACK_SENT:
            if (!tcphead->syn && !tcphead->fin)
            {
                // printk("Server completed handshake\n");
                entry->connstate = ESTABLISHED;
                return NF_ACCEPT;
            }
            return NF_DROP;
        case ESTABLISHED:
            if (!tcphead->syn && tcphead->fin)
            {
                // printk("Client initiated FIN\n");
                entry->connstate = CLIENT_SENT_FIN;
            }
            // printk("Client->server conn packet\n");
            return NF_ACCEPT;
        case CLIENT_SENT_FIN:
            if (tcphead->fin)
            {
                // printk("Client resent FIN\n");
                return NF_ACCEPT;
            }
            return NF_DROP;
        case SERVER_ACCEPTED_FIN:
            if (!tcphead->syn && !tcphead->fin)
            {
                // printk("Second FIN Acknowledged, Removing connection\n");
                list_del(&entry->list);
                kfree(entry);
                conncount--;
                return NF_ACCEPT;
            }
            return NF_DROP;
        default:
            // printk("C->S default dropped, SYN: %d FIN: %d RST: %d\n", tcphead->syn, tcphead->fin, tcphead->rst);
            return NF_DROP;
        }
    }
    // UNREACHABLE
}

void conn_add(__be32 sip, __be32 dip, __be16 sport, __be16 dport, connstate_t initstate)
{
    conn_entry *newentry = kzalloc(sizeof(conn_entry), GFP_KERNEL);
    newentry->cl_ip = sip;
    newentry->sv_ip = dip;
    newentry->cl_port = sport;
    newentry->sv_port = dport;
    newentry->connstate = initstate;
    INIT_LIST_HEAD(&newentry->list);
    list_add_tail(&newentry->list, &connlist);
    // printk("Added new TCP connection from %pI4 to %pI4\n", &newentry->cl_ip, &newentry->sv_ip);
    conncount++;
    // printk("There are currently %u connections\n", conncount);
}

conn_entry *conn_get_raw(__be32 sip, __be16 sport, __be32 dip, __be16 dport)
{
    conn_entry *iter;

    list_for_each_entry(iter, &connlist, list)
    {
        if (iter->cl_ip == sip && iter->cl_port == sport && iter->sv_ip == dip && iter->sv_port == dport)
        {
            return iter;
        }
        else if (iter->sv_ip == sip && iter->sv_port == sport && iter->cl_ip == dip && iter->cl_port == dport)
        {
            return iter;
        }
    }
    return NULL;
}

inline conn_entry *conn_get(struct iphdr *iphead, struct tcphdr *tcphead)
{
    return conn_get_raw(iphead->saddr, tcphead->source, iphead->daddr, tcphead->dest);
}

void conn_set_mitm(struct iphdr *iphead, struct tcphdr *tcphead, __be16 port)
{
    conn_entry *conn = conn_get(iphead, tcphead);
    if (conn != NULL)
        conn->mitm_port = port;
}

ssize_t setmitm_iface(struct device *dev, struct device_attribute *attr,
                      const char *buf, size_t count)
{
    if (count != sizeof(struct mitm_input))
        return 0;

    struct mitm_input *mti = (struct mitm_input *)buf;
    conn_entry *conn = conn_get_raw(mti->clip, mti->clport, mti->svip, mti->svport);
    if (conn == NULL)
    {
        // printk("Failed to update mitm\n");
        return 0;
    }
    conn->mitm_port = mti->mitmport;
    // printk("Updated mitm port %d\n", ntohs(conn->mitm_port));
    return sizeof(struct mitm_input);
}

ssize_t add_ftpport(struct device *dev, struct device_attribute *attr,
                    const char *buf, size_t count)
{
    if (count != 2){
        // printk("Wrong count: %u\n", count);
        return 0;
    }
    if(ftpcount >= MAX_CONNS){
        // printk("Too many ftp connections\n");
        return 0;
    }
    
    __be16 port = *(__be16 *)buf;    
    ftpports[ftpcount] = port;
    ftpcount++;

    // printk("\e[34mftp port %d added\e[m\n", ntohs(port));
    return 2;
}

struct mitm_data conn_get_mitm(__be16 mitm_port)
{
    conn_entry *iter;
    struct mitm_data out = {0, 0};

    list_for_each_entry(iter, &connlist, list)
    {
        if (iter->mitm_port == mitm_port)
        {
            out.clport = iter->cl_port;
            out.svport = iter->sv_port;
            return out;
        }
    }
    return out;
    // Note: struct small enough (32-bit) to be returned by value
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
};

#define CONNDEV_NAME "conndev"
int conndev_major = 0;
static struct device *conndev_sysfs = NULL;
const struct device_attribute connsdev = __ATTR(conns, S_IRUGO, conns_show, NULL);
const struct device_attribute mitmdev = __ATTR(mitm, S_IWUSR, NULL, setmitm_iface);
const struct device_attribute ftpdev = __ATTR(ftp, S_IWUSR, NULL, add_ftpport);

int create_conndev(void)
{

    conndev_major = register_chrdev(0, CONNDEV_NAME, &fops);
    if (conndev_major < 0)
        return -1;

    conndev_sysfs = device_create(firewall_class, NULL, MKDEV(conndev_major, 0), NULL,
                                  "conns");
    if (IS_ERR_VALUE(conndev_sysfs))
    {
        unregister_chrdev(conndev_major, "conns");
        return -1;
    }
    if (device_create_file(conndev_sysfs, &connsdev))
    {
        device_destroy(firewall_class, MKDEV(conndev_major, 0));
        unregister_chrdev(conndev_major, CONNDEV_NAME);
        return -1;
    }
    if (device_create_file(conndev_sysfs, &mitmdev))
    {
        device_remove_file(conndev_sysfs, &connsdev);
        device_destroy(firewall_class, MKDEV(conndev_major, 0));
        unregister_chrdev(conndev_major, CONNDEV_NAME);
        return -1;
    }
    if (device_create_file(conndev_sysfs, &ftpdev))
    {
        device_remove_file(conndev_sysfs, &mitmdev);
        device_remove_file(conndev_sysfs, &connsdev);
        device_destroy(firewall_class, MKDEV(conndev_major, 0));
        unregister_chrdev(conndev_major, CONNDEV_NAME);
        return -1;
    }
    // printk("All devices created\n");
    return 0;
}

void destroy_conndev(void)
{
    conn_entry *iter, *next;

    list_for_each_entry_safe(iter, next, &connlist, list)
    {
        list_del(&iter->list);
        kfree(iter);
    }
    conncount = 0;

    device_remove_file(conndev_sysfs, &ftpdev);
    device_remove_file(conndev_sysfs, &mitmdev);
    device_remove_file(conndev_sysfs, &connsdev);
    device_destroy(firewall_class, MKDEV(conndev_major, 0));
    unregister_chrdev(conndev_major, CONNDEV_NAME);
}