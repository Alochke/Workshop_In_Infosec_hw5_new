#include "fw.h"
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/device.h>
#include <linux/fs.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/udp.h>
#include <net/tcp.h>
#include <stdbool.h>

MODULE_LICENSE("GPL");

struct class *firewall_class = NULL;

extern rule_t rule_table[MAX_RULES];
extern __u32 rule_count;

/* Create a proxy for the given ip */
void add_proxy_2(__be32 sip, __be16 sport, __be32 dip, __be16 dport, struct sk_buff *skb)
{
    struct iphdr *ip_head = ip_hdr(skb);
    struct tcphdr *tcp_head = tcp_hdr(skb);

    if (sip != 0)
        ip_head->saddr = sip;
    if (dip != 0)
        ip_head->daddr = dip;

    if (sport != 0)
        tcp_head->source = sport;
    if (dport != 0)
        tcp_head->dest = dport;

    // Fixing checksum -- based on the Github example
    ip_head->check = 0;
    ip_head->check = ip_fast_csum((u8 *)ip_head, ip_head->ihl);

    skb->ip_summed = CHECKSUM_NONE;
    skb->csum_valid = 0;

    skb_linearize(skb);
    ip_head = ip_hdr(skb);
    tcp_head = tcp_hdr(skb);

    // Fix TCP header checksum
    int tcplen = (ntohs(ip_head->tot_len) - ((ip_head->ihl) << 2));
    tcp_head->check = 0;
    tcp_head->check = tcp_v4_check(tcplen, ip_head->saddr, ip_head->daddr, csum_partial((char *)tcp_head, tcplen, 0));
}

void add_proxy(__be32 nip, __be16 nport, struct sk_buff *skb, bool csrc, bool cport)
{
    struct iphdr *ip_head = ip_hdr(skb);
    struct tcphdr *tcp_head = tcp_hdr(skb);
    // printk("Proxying %s %pI4:%u to %pI4:%u\n", 
    //     csrc ? "src" : "dst",
    //     csrc ? &ip_head->saddr : &ip_head->daddr,
    //     csrc ? ntohs(tcp_head->source) : ntohs(tcp_head->dest),
    //     &nip,
    //     cport ? ntohs(nport) : 1337000);

    add_proxy_2(csrc ? nip : 0, (csrc && cport) ? nport : 0, csrc ? 0 : nip, (!csrc && cport) ? nport : 0, skb);
}

#define IPADDRS(x, y, z, w) (x + (y << 8) + (z << 16) + (w << 24))

#define CLIENT_IP IPADDRS(10, 1, 1, 1)
#define SERVER_IP IPADDRS(10, 1, 2, 2)

#define FW_CLIENT_IP IPADDRS(10, 1, 1, 3)
#define FW_SERVER_IP IPADDRS(10, 1, 2, 3)

// Hook function for pre-routing
unsigned int route_hook(void *priv, struct sk_buff *skb,
                        const struct nf_hook_state *state)
{
    __u16 ack = 0;
    int interface = 0;
    log_row_t logrow = {0};

    // We know that packets in the hook are IPv4...
    struct iphdr *ip_head = ip_hdr(skb);
    logrow.dst_ip = ip_head->daddr;
    logrow.src_ip = ip_head->saddr;
    logrow.protocol = ip_head->protocol;

    if (logrow.protocol != PROT_ICMP && logrow.protocol != PROT_TCP && logrow.protocol != PROT_UDP)
    {
        return NF_ACCEPT; // Do not log such packets
    }
    if ((logrow.dst_ip & 0x000000FF) == 0x0000007F) // apply big-endian mask
        return NF_ACCEPT;                           // Auto-accept loopback
    if (strcmp(skb->dev->name, "eth1") == 0 || strcmp(skb->dev->name, "enp0s8") == 0)
    {
        interface = DIRECTION_OUT;
    }
    else if (strcmp(skb->dev->name, "eth2") == 0 || strcmp(skb->dev->name, "enp0s9") == 0)
    {
        interface = DIRECTION_IN;
    }

    if (logrow.protocol == PROT_TCP)
    {
        struct tcphdr *tcp_head = tcp_hdr(skb);
        printk("Local out %pI4:%u to %pI4:%u with SYN %d ACK %d FIN %d RST %d", &ip_hdr(skb)->saddr, ntohs(tcp_hdr(skb)->source),
                    &ip_hdr(skb)->daddr, ntohs(tcp_hdr(skb)->dest), tcp_head->syn, tcp_head->ack, tcp_head->fin, tcp_head->rst);
        if (tcp_head->fin && tcp_head->urg && tcp_head->psh)
        {
            logrow.reason = REASON_XMAS_PACKET;
            logrow.action = NF_DROP;
            log_filter(&logrow);
            return NF_DROP;
        }
        logrow.dst_port = tcp_head->dest;
        logrow.src_port = tcp_head->source;

        if (tcp_head->ack)
        {
            // Skip static rule checking
            unsigned int conn_res = NF_DROP;
            if (tcp_head->syn)
            {
                // printk("SYN-ACK\n");
            }
            if (interface == DIRECTION_OUT)
            {
                
                // c->f
                if(tcp_head->source == ntohs(80))
                {
                    // We already filter them on the way out
                    printk("idk %pI4:%u to %pI4:%u\n", &ip_hdr(skb)->saddr, ntohs(tcp_hdr(skb)->source),
                    &ip_hdr(skb)->daddr, ntohs(tcp_hdr(skb)->dest));
                    add_proxy(FW_CLIENT_IP, 0, skb, false, false);
                    return NF_ACCEPT;
                }

                conn_res = conn_filter(ip_head, tcp_head);
                if (conn_res == NF_ACCEPT && tcp_head->dest == ntohs(80))
                {
                    add_proxy(FW_CLIENT_IP, ntohs(800), skb, false, true);
                }
                else if (conn_res == NF_ACCEPT && tcp_head->dest == ntohs(21))
                {
                    add_proxy(FW_CLIENT_IP, ntohs(210), skb, false, true);
                }
            }
            else if (interface == DIRECTION_IN)
            {
                // s->f
                if (tcp_head->source == ntohs(80) || tcp_head->source == ntohs(21))
                {
                    // We already filter them on the way out
                    add_proxy(FW_SERVER_IP, 0, skb, false, false);
                    return NF_ACCEPT;
                }
                conn_res = conn_filter(ip_head, tcp_head);
                if (conn_res == NF_ACCEPT && tcp_head->dest == ntohs(80))
                {
                    add_proxy(FW_SERVER_IP, ntohs(15), skb, false, true);
                }
            }

            return conn_res;
        }
        else if (tcp_head->syn)
        {            
            // printk("SYN\n");

            bool isftp=false;
            for(size_t i=0;i<ftpcount;++i){
                if(ftpports[i] == tcp_head->dest)
                {
                    isftp=true;
                    break;
                }
            }
            if(isftp){
                // printk("\e[34mFTP active syn %u to %u\e[m\n",ntohs(tcp_head->source), ntohs(tcp_head->dest));
                conn_add(ip_head->saddr, ip_head->daddr, tcp_head->source, tcp_head->dest, HANDSHAKE_SYN_SENT);
                return NF_ACCEPT;
            }                        
        }
            
        ack = tcp_head->ack + 1; // 0x01 for 0, 0x02 for 1
    }
    else if (logrow.protocol == PROT_UDP)
    {
        struct udphdr *udp_head = udp_hdr(skb);
        logrow.dst_port = udp_head->dest;
        logrow.src_port = udp_head->source;
    }

    for (int i = 0; i < rule_count; ++i)
    {
        rule_t rule = rule_table[i];
        if (!(rule.direction & interface))
            continue;
        if (rule.protocol != PROT_ANY && rule.protocol != logrow.protocol)
            continue;
        if ((rule.src_ip & rule.src_prefix_mask) != (logrow.src_ip & rule.src_prefix_mask) || (rule.dst_ip & rule.dst_prefix_mask) != (logrow.dst_ip & rule.dst_prefix_mask))
            continue;
        if (rule.src_port != PORT_ANY && rule.src_port != htons(PORT_ABOVE_1023) && rule.src_port != logrow.src_port)
            continue;

        else if (rule.src_port == htons(PORT_ABOVE_1023) && logrow.src_port <= 1023)
            continue;

        if (rule.dst_port != PORT_ANY && rule.dst_port != htons(PORT_ABOVE_1023) && rule.dst_port != logrow.dst_port)
            continue;
        else if (rule.dst_port == htons(PORT_ABOVE_1023) && logrow.dst_port <= 1023)
            continue;
        if (rule.protocol == PROT_TCP && !(rule.ack & ack))
            continue;
        // If we reached here, the rule is relevant
        if (logrow.protocol == PROT_TCP && rule.action == NF_ACCEPT)
        {
            struct tcphdr *tcp_head = tcp_hdr(skb);

            if (interface == DIRECTION_OUT)
            {
                if (tcp_head->dest == ntohs(80))
                {
                    // printk("HTTP syn proxy\n");
                    add_proxy(FW_CLIENT_IP, ntohs(800), skb, false, true);
                }
                else if (tcp_head->dest == ntohs(21))
                {
                    add_proxy(FW_CLIENT_IP, ntohs(210), skb, false, true);
                }
            }
            else if(interface == DIRECTION_IN)
            {
                if (tcp_head->dest == ntohs(80))
                {
                    // printk("HTTP syn proxy\n");
                    add_proxy(FW_SERVER_IP, ntohs(15), skb, false, true);
                }
            }
            conn_entry *maybe_conn = conn_get(ip_head, tcp_head);
            if (maybe_conn == NULL || maybe_conn->connstate != HANDSHAKE_SYN_SENT)
                conn_add(logrow.src_ip, logrow.dst_ip, logrow.src_port, logrow.dst_port, HANDSHAKE_SYN_SENT);
        }
        logrow.reason = i;
        logrow.action = rule.action;
        log_filter(&logrow);
        return rule.action;
    }
    logrow.reason = REASON_NO_MATCHING_RULE;
    logrow.action = NF_DROP;
    log_filter(&logrow);
    return NF_DROP;
}

// Local-out hook
unsigned int localout_hook(void *priv, struct sk_buff *skb,
                           const struct nf_hook_state *state)
{
    struct iphdr *iphead = ip_hdr(skb);
    if (iphead->protocol != PROT_TCP)
        return NF_ACCEPT;
    struct tcphdr *tcphead = tcp_hdr(skb);

    // printk("Local out %pI4:%u to %pI4:%u with SYN %d ACK %d FIN %d RST %d", &iphead->saddr, ntohs(tcphead->source),
    //        &iphead->daddr, ntohs(tcphead->dest), tcphead->syn, tcphead->ack, tcphead->fin, tcphead->rst);

    // Note - the only local-out packets to the client/server should be from proxy
    if (iphead->daddr == CLIENT_IP)
    {
        // printk("Conn-filtering local-out\n");
        if (tcphead->source == htons(800))
            add_proxy(SERVER_IP, htons(80), skb, true, true);
        else if (tcphead->source == htons(210))
            add_proxy(SERVER_IP, htons(21), skb, true, true);
        else
            add_proxy(SERVER_IP, 0, skb, true, false);

        conn_filter(ip_hdr(skb), tcp_hdr(skb));
    }
    else if (iphead->daddr == SERVER_IP)
    {
        // printk("Conn-filtering local-out\n");
        if (tcphead->source == htons(15))
            add_proxy(CLIENT_IP, htons(80), skb, true, true);
        else
            add_proxy(CLIENT_IP, 0, skb, true, false);

        conn_filter(ip_hdr(skb), tcp_hdr(skb));
    }

    // printk("idk %pI4:%u to %pI4:%u\n", &ip_hdr(skb)->saddr, ntohs(tcp_hdr(skb)->source),
    //        &ip_hdr(skb)->daddr, ntohs(tcp_hdr(skb)->dest));

    return NF_ACCEPT;
}

const struct nf_hook_ops hook1 = {
    .hook = route_hook,
    .pf = NFPROTO_IPV4,
    .hooknum = NF_INET_PRE_ROUTING,
    .priority = NF_IP_PRI_FIRST,
};

const struct nf_hook_ops hook2 = {
    .hook = localout_hook,
    .pf = NFPROTO_IPV4,
    .hooknum = NF_INET_LOCAL_OUT,
    .priority = NF_IP_PRI_FIRST,
};

static int __init fw_module_init(void)
{
    int err = 0;

    err = create_iodev();
    if (err < 0)
        return err;

    err = create_conndev();
    if (err < 0)
        return err;

    err = create_logdev();
    if (err < 0)
        return err;

    // Register hooks and handle errors
    err = nf_register_net_hook(&init_net, &hook1);
    err = nf_register_net_hook(&init_net, &hook2);

    if (err < 0)
    {
        // printk("Register hooks failed\n");
        return err;
    }
    printk(KERN_INFO "Module loaded\n");

    return 0;
}

static void __exit fw_module_exit(void)
{
    // Unregister hooks
    nf_unregister_net_hook(&init_net, &hook1);
    nf_unregister_net_hook(&init_net, &hook2);

    destroy_logdev();
    destroy_conndev();
    destroy_iodev();
    printk(KERN_INFO "Module unloaded\n");
}

module_init(fw_module_init);
module_exit(fw_module_exit);