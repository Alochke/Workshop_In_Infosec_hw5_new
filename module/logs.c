#pragma GCC diagnostic ignored "-Wdeclaration-after-statement"

#include "fw.h"
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/device.h>
#include <linux/list.h>
#include <linux/uaccess.h>
#include <linux/timekeeping32.h>

struct log_entry
{
    log_row_t logrow;
    struct list_head list;
};

int logsize = 0;
static LIST_HEAD(entrylist);

void log_filter(log_row_t *newrow)
{
    struct log_entry *row;
    bool found = false;
    struct timespec ts;

    list_for_each_entry(row, &entrylist, list)
    {
        // Check if row already exists
        if (newrow->src_ip == row->logrow.src_ip && newrow->dst_ip == row->logrow.dst_ip && newrow->src_port == row->logrow.src_port &&
            newrow->dst_port == row->logrow.dst_port && newrow->protocol == row->logrow.protocol)
        {

            found = true;
            row->logrow.count++; // Increase count
            getnstimeofday(&ts);
            row->logrow.timestamp = ts.tv_sec; // Update timestamp
            break;
        }
    }
    if (!found)
    {
        struct log_entry *newentry = kmalloc(sizeof(struct log_entry), GFP_KERNEL);
        newrow->count = 1;
        getnstimeofday(&ts);
        newrow->timestamp = ts.tv_sec; // Update timestamp

        memcpy(&newentry->logrow, newrow, sizeof(log_row_t));
        INIT_LIST_HEAD(&newentry->list);
        list_add_tail(&newentry->list, &entrylist);
        logsize++;
    }
}

int logdev_major;

bool startread;
struct log_entry *next_row;

int logs_open(struct inode *inode1, struct file *fileobj)
{
    startread = false;
    next_row = NULL;

    return 0;
}

ssize_t logs_read(struct file *fileobj, char *buff, size_t count, loff_t *offset)
{
    if (!startread)
    {
        if (count < sizeof(logsize))
            return -1;

        *((int *)buff) = logsize;
        next_row = list_entry(entrylist.next, struct log_entry, list); // First row
        startread = true;
        return sizeof(logsize);
    }

    // For simplicity can only read one row at a time
    if (count != sizeof(log_row_t))
        return -1;

    // Cannot read empty log
    if (logsize < 1)
        return 0;

    if (copy_to_user(buff, &next_row->logrow, sizeof(log_row_t)))
    {
        return -1;
    }

    next_row = list_entry(next_row->list.next, struct log_entry, list);

    return sizeof(log_row_t);
}

void clear_log(void){
    struct list_head *iter;
    struct list_head *tmpstor;
    struct log_entry *row;

    // Clear the log entries
    list_for_each_safe(iter, tmpstor, &entrylist)
    {
        row = list_entry(iter, struct log_entry, list);
        list_del(&row->list);
        kfree(row);
    }
}

ssize_t logreset_store(struct device *dev, struct device_attribute *attr,
                       const char *buf, size_t count)
{    
    clear_log();

    logsize = 0;
    startread = 0;
    next_row = NULL;

    return count;
}

static struct device *log_sysfs = NULL;
static struct device *log_sysfs2 = NULL;
const struct device_attribute logreset = __ATTR(reset, S_IWUSR, NULL, logreset_store);

struct file_operations logfops = {
    .owner = THIS_MODULE,
    .open = logs_open,
    .read = logs_read,
};

int create_logdev(void)
{
    logdev_major = register_chrdev(0, "fw_log", &logfops);

    if (logdev_major < 0)
        return -1;

    log_sysfs = device_create(firewall_class, NULL, MKDEV(logdev_major, 0), NULL,
                              DEVICE_NAME_LOG);
    if (IS_ERR_VALUE(log_sysfs))
        return -1;

    if (device_create_file(log_sysfs, &logreset))
        return -1;

    log_sysfs2 = device_create(firewall_class, NULL, MKDEV(logdev_major, 1), NULL, "fw_log");

    return 0;
}

void destroy_logdev(void)
{
    clear_log();

    device_remove_file(log_sysfs, &logreset);
    device_destroy(firewall_class, MKDEV(logdev_major, 0));
    device_destroy(firewall_class, MKDEV(logdev_major, 1));

    unregister_chrdev(logdev_major, "fw_log");
}