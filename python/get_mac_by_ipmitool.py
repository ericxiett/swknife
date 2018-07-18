import commands
import sys


def main():
    print('Get mac info by ipmitool...')

    if len(sys.argv) < 2:
        print('Please input ipmi address!')
        exit(1)

    ipmi_addr = sys.argv[1]
    # print('   ipmi addr: %s' % ipmi_addr)

    cmd_on_board = 'ipmitool -I lanplus -H ' + \
        ipmi_addr + ' -U admin -P admin raw 0x3a 0x02 0x04 0x00 0x01'
    ob_ret = commands.getoutput(cmd_on_board)
    if 'Unable' in ob_ret:
        print('Can not get on board macs')
        exit(1)
    # print('on board raw info: %s' % ob_ret)
    ob_list = ob_ret.split(' ')
    ob_mac1 = ' '.join(ob_list[6:12])
    print('ob_mac1: %s' % ob_mac1)
    ob_mac2 = ' '.join(ob_list[18:24])
    print('ob_mac2: %s' % ob_mac2)

    cmd_out_board = 'ipmitool -I lanplus -H ' + \
        ipmi_addr + ' -U admin -P admin raw 0x3a 0x02 0x0b 0x00 0x03'
    outb_ret = commands.getoutput(cmd_out_board)
    if 'Unable' in outb_ret:
        print('Can not get out board macs')
        exit(1)
    # print('out board raw info: %s' % outb_ret)
    outb_list = outb_ret.strip().replace("\n", "").split(' ')
    try:
        outb_mac1 = ' '.join(outb_list[6:12])
        print('out_board_mac1: %s' % outb_mac1)
        outb_mac2 = ' '.join(outb_list[19:25])
        print('out_board_mac2: %s' % outb_mac2)
        outb_mac3 = ' '.join(outb_list[32:38])
        print('out_board_mac3: %s' % outb_mac3)
        outb_mac4 = ' '.join(outb_list[45:51])
        print('out_board_mac4: %s' % outb_mac4)
    except Exception as e:
        print('Got error %s ' % e)
        exit(1)


if __name__ == '__main__':
    sys.exit(main())
