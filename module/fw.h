#ifndef _FW_H_
#define _FW_H_

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


// the protocols we will work with
typedef enum {
	PROT_ICMP	= 1,
	PROT_TCP	= 6,
	PROT_UDP	= 17,
	PROT_OTHER 	= 255,
	PROT_ANY	= 143,
} prot_t;


// various reasons to be registered in each log entry
typedef enum {
	REASON_FW_INACTIVE           = -1,
	REASON_NO_MATCHING_RULE      = -2,
	REASON_XMAS_PACKET           = -4,
	REASON_ILLEGAL_VALUE         = -6,
} reason_t;
	

// auxiliary strings, for your convenience
#define DEVICE_NAME_RULES			"rules"
#define DEVICE_NAME_LOG				"log"
#define DEVICE_NAME_CONN_TAB		"conn_tab"
#define CLASS_NAME					"fw"
#define LOOPBACK_NET_DEVICE_NAME	"lo"
#define IN_NET_DEVICE_NAME			"eth1"
#define OUT_NET_DEVICE_NAME			"eth2"

// auxiliary values, for your convenience
#define IP_VERSION		(4)
#define PORT_ANY		(0)
#define PORT_ABOVE_1023	(1023)
#define MAX_RULES		(50)

// device minor numbers, for your convenience
typedef enum {
	MINOR_RULES    = 0,
	MINOR_LOG      = 1,
} minor_t;

typedef enum {
	ACK_NO 		= 0x01,
	ACK_YES 	= 0x02,
	ACK_ANY 	= ACK_NO | ACK_YES,
} ack_t;

typedef enum {
	DIRECTION_IN 	= 0x01,
	DIRECTION_OUT 	= 0x02,
	DIRECTION_ANY 	= DIRECTION_IN | DIRECTION_OUT,
} direction_t;

// rule base
typedef struct {
	char rule_name[20];			// names will be no longer than 20 chars
	direction_t direction;
	__be32	src_ip;
	__be32	src_prefix_mask; 	// e.g., 255.255.255.0 as int in the local endianness
	__u8    src_prefix_size; 	// valid values: 0-32, e.g., /24 for the example above
								// (the field is redundant - easier to print)
	__be32	dst_ip;
	__be32	dst_prefix_mask; 	// as above
	__u8    dst_prefix_size; 	// as above	
	__be16	src_port; 			// number of port or 0 for any or port 1023 for any port number > 1023  
	__be16	dst_port; 			// number of port or 0 for any or port 1023 for any port number > 1023 
	__u8	protocol; 			// values from: prot_t
	ack_t	ack; 				// values from: ack_t
	__u8	action;   			// valid values: NF_ACCEPT, NF_DROP
} __attribute__((packed)) rule_t;

// logging
typedef struct {
	unsigned long  	timestamp;     	// time of creation/update
	unsigned char  	protocol;     	// values from: prot_t
	unsigned char  	action;       	// valid values: NF_ACCEPT, NF_DROP
	__be32   		src_ip;		  	// if you use this struct in userspace, change the type to unsigned int
	__be32			dst_ip;		  	// if you use this struct in userspace, change the type to unsigned int
	__be16 			src_port;	  	// if you use this struct in userspace, change the type to unsigned short
	__be16 			dst_port;	  	// if you use this struct in userspace, change the type to unsigned short
	reason_t     	reason;       	// rule#index, or values from: reason_t
	unsigned int   	count;        	// counts this line's hits
} __attribute__((packed)) log_row_t;

typedef enum _connstate
{
    HANDSHAKE_SYN_SENT,      // SYN_SENT, LISTEN
    HANDSHAKE_SYNACK_SENT,   // SYN_SENT, SYN_RECEIVED
    ESTABLISHED,             // ESTABLISHED, ESTABLISHED
    CLIENT_SENT_FIN,         // FIN_WAIT_1, CLOSE_WAIT
    SERVER_ACKNOWLEDGED_FIN, // FIN_WAIT_2, CLOSE_WAIT
    SERVER_ACCEPTED_FIN      // FIN_WAIT_2, LAST_ACK

} __attribute__((packed)) connstate_t;

typedef struct _conn_entry
{
    __be32 cl_ip;
    __be32 sv_ip;
    __be16 cl_port;
    __be16 sv_port;
    __be16 mitm_port;
    connstate_t connstate;
    struct list_head list;
} __attribute__((packed)) conn_entry;

struct mitm_data{
	__be16 clport;
	__be16 svport;
};

// Required to ensure all entries fit sysfs driver buffer
#define MAX_CONNS ((PAGE_SIZE - 4) / sizeof(conn_entry))

extern struct class *firewall_class;
extern __be16 ftpports[MAX_CONNS];
extern size_t ftpcount;

void log_filter(log_row_t *newrow);

int create_logdev(void);
void destroy_logdev(void);

int create_iodev(void);
void destroy_iodev(void);

int create_conndev(void);
void destroy_conndev(void);

unsigned int conn_filter(struct iphdr *, struct tcphdr *);
void conn_set_mitm(struct iphdr *, struct tcphdr *, __be16);
struct mitm_data conn_get_mitm(__be16 mitm_port);
void conn_add(__be32 sip, __be32 dip, __be16 sport, __be16 dport, connstate_t initstate);
conn_entry *conn_get(struct iphdr *iphead, struct tcphdr *tcphead);



#endif // _FW_H_