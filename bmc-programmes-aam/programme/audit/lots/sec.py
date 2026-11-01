import glob,re,sys
H=r'(VISITORS|RECENT VISITORS|LAST WEEK.S VISITORS|ARRIVALS|DEPARTURES|ANNOUNCEMENTS|PAST EVENTS|EVENTS OF LAST WEEK|NEW STUDENTS?|NOTES|STAFF ADDITIONS|Due to Arrive|Departing|WORK (SUMMARY|CREW REPORTS|REPORTS)|REPORT ON HIRED WORK)'
n=int(sys.argv[1])
for inv in sys.argv[2:]:
    f=glob.glob(f'pages_txt/*/2017.40.{inv}_*')[0]; s=re.sub(r'\s+',' ',open(f).read())
    for m in re.finditer(H, s):
        print(f'== {inv} @{m.start()}:', s[m.start():m.start()+n])
