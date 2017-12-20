import MySQLdb
from base64 import b64encode
import getopt
import sys

def usage():
    print "python query_db_for_gyms.py -u <db-user> -p <passwd> -h <db-host> -d <database>"
    sys.exit(0)


def main():
    host=""
    database=""
    user=""
    passwd=""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:h:u:p:", ["help", "output="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for o, a in opts:
        if o == "-u":
            user = str(a)
        elif o == "-d":
            database = str(a)
        elif o == "-p":
            passwd = str(a)
        elif o == "-h":
            host = str(a)
        else:
            assert False, "unhandled option"

    print "Host    : " + host
    print "User    : " + user
    print "Password: " + passwd
    print "Database: " + database

    if host == "" or database == "" or user == "" or passwd == "":
        print "ERROR, something was not provided on the command line"
        usage()
        sys.exit(-1)


    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=database)
    cur = db.cursor()

    cmd = "SELECT gym_id,latitude,longitude FROM gym"

    cur.execute(cmd)

    for i in cur:
        print b64encode(i[0]) + "," + str(i[0]) + ",<INSERT-NAME-HERE>," + str(i[1]) + "," + str(i[2])

if __name__ == '__main__':
    main()

