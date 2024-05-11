#pragma GCC diagnostic ignored "-Wdeclaration-after-statement"
#pragma GCC diagnostic ignored "-Wenum-compare"

#include "fw.h"
#include <linux/string.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/uaccess.h>

#define chrdev_name "tmp"

rule_t rule_table[MAX_RULES];
__u32 rule_count = 0;

int major_n;
static struct device *sysfs_dev = NULL;

ssize_t dev_store(struct device *dev, struct device_attribute *attr,
                  const char *buf, size_t count)
{
    int i;
    __u32 tmp_count = *(__u32 *)buf;
    __u32 tocopy;
    if (tmp_count > MAX_RULES)
    {
        return 0;
    }
    tocopy = sizeof(rule_t) * tmp_count;
    if (count < tocopy + 4)
    {
        return 0;
    }
    for (i = 0; i < tmp_count; ++i)
    {
        rule_t *crule = (rule_t *)(buf + 4 + sizeof(rule_t) * i);
        if (strnlen(crule->rule_name, 20) > 19)
            break;
        if (crule->direction < DIRECTION_IN || crule->direction > DIRECTION_ANY)
            break;
        if (crule->src_prefix_size > 32 || crule->dst_prefix_size > 32)
            break;
        crule->src_prefix_mask = htonl(~((1 << (32 - crule->src_prefix_size)) - 1));
        crule->dst_prefix_mask = htonl(~((1 << (32 - crule->dst_prefix_size)) - 1));
        if (crule->src_prefix_size == 0)
            crule->src_prefix_mask = 0;
        if (crule->dst_prefix_size == 0)
            crule->dst_prefix_mask = 0;

        if (ntohs(crule->src_port) > 1023 || ntohs(crule->dst_port) > 1023)
            break;
        if (crule->protocol != PROT_ANY && crule->protocol != PROT_ICMP && crule->protocol != PROT_OTHER && crule->protocol != PROT_TCP && crule->protocol != PROT_UDP)
            break;
        if (crule->direction < ACK_NO || crule->direction > ACK_ANY)
            break;
        if (crule->action != NF_ACCEPT && crule->action != NF_DROP)
            break;
    }
    if (i < tmp_count)
        return 0;
    memcpy(rule_table, buf + 4, tocopy);
    rule_count = tmp_count;
    return count;
}

ssize_t dev_show(struct device *dev, struct device_attribute *attr, char *buf)
{
    *((__u32 *)buf) = rule_count;

    memcpy(buf + 4, rule_table, sizeof(rule_t) * rule_count);
    return sizeof(rule_t) * rule_count + 4;
}

const struct file_operations fops = {
    .owner = THIS_MODULE,
};

const struct device_attribute rulesdev = __ATTR(rules, S_IRUGO | S_IWUSR, dev_show, dev_store);

int create_iodev(void)
{
    int err;
    int res;

    major_n = register_chrdev(0, chrdev_name, &fops);
    if (major_n < 0)
    {
        return -1;
    }

    firewall_class = class_create(THIS_MODULE, CLASS_NAME);
    if (IS_ERR_VALUE(firewall_class))
    {
        err = -1;
        goto cleanup_chrdev;
    }

    sysfs_dev = device_create(firewall_class, NULL, MKDEV(major_n, 0), NULL,
                              DEVICE_NAME_RULES);
    if (IS_ERR_VALUE(sysfs_dev))
    {
        err = -1;
        goto cleanup_class;
    }

    res = device_create_file(sysfs_dev, &rulesdev);
    if (res)
    {
        err = -1;
        goto cleanup_devices;
    }
    if (err == 0)
        return 0;

cleanup_devices:
    device_destroy(firewall_class, MKDEV(major_n, 0));
cleanup_class:
    class_destroy(firewall_class);
cleanup_chrdev:
    unregister_chrdev(major_n, chrdev_name);

    return err;
}

void destroy_iodev(void)
{
    device_remove_file(sysfs_dev, &rulesdev);
    device_destroy(firewall_class, MKDEV(major_n, 0));
    class_destroy(firewall_class);
    unregister_chrdev(major_n, chrdev_name);
}