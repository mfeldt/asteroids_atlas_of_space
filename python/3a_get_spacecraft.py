import telnetlib
import pandas as pd
import time, datetime
import os

from astroquery.jplhorizons import Horizons

def get_spacecraft():
    tn=telnetlib.Telnet('horizons.jpl.nasa.gov',port=6775)
    print(repr(tn.read_until(b"Horizons> ")))
    tn.write(b"PAGE\n")
    print(repr(tn.read_until(b"Horizons> ")))
    tn.write(b"MB\n")
    tn.write(b"\n")
    raw_answer = tn.read_until(b"Horizons> ")
    tn.write(b"QUIT\n")
    print(tn.read_all())
    lines = str(raw_answer).split("\\r\\n")
    spacecraft_lines = [l for l in lines if "space" in l]

    hid   = []
    name  = []
    for line in spacecraft_lines:
        print(line)
        hid.append(line.split()[0])
        name.append(" ".join(line.split()[1:]).split('(space')[0].strip())

    df = pd.DataFrame({"hid":hid,"name":name})
    return(df)

def get_all_info(df):
    full_name = []
    end_time = []
    begin_time = []
    drop_indexes= []

    today_string = datetime.datetime.now().strftime("%Y-%m-%d")
    for index,row in df.iterrows():
        ##
        ## provoke an error getting very early ephemeris
        ##
        print(index,row)
        try:
            obj = Horizons(id=row['hid'],epochs={'start':'1515-01-01','stop':today_string,'step':'1d'})
            eph=obj.ephemerides()
        except:
            errline =  obj.raw_response.split('\n')[-2]
            print(errline)
            try:
                full_name.append(errline.split('"')[1])
                begin_time.append(errline.split('prior to A.D.')[1])
            except:
                print("Dropping object %s"%index)
                drop_indexes.append(index)
                continue
        ##
        ## another one for the far future
        ##
        try:
            obj = Horizons(id=row['hid'],epochs={'start':today_string,'stop':'3020-01-01','step':'1d'})
            eph=obj.ephemerides()
        except:
            errline =  obj.raw_response.split('\n')[-2]
            print(errline)
            try:
                end_time.append(errline.split('after A.D.')[1])
            except:
                end_time.append("")
        time.sleep(1.0) # do not overrun the server

    if len(full_name)+len(drop_indexes) != len(df):
        print("Lengths do not match up!")
    if len(full_name) != len(end_time):
        print("Somehow, there are more or fewer end_times than names!")

    if len(drop_indexes)>0:
        df = df.drop(drop_indexes,axis=0)
    df['full_name']  = full_name
    df['begin_time'] = begin_time
    df['end_time']   = end_time
    return(df)


df = get_spacecraft()
#df.to_pickle('spacecraft.pickle')
#df = pd.read_pickle('spacecraft.pickle')
df=get_all_info(df)
out_file = os.path.join(os.path.abspath(__file__),'..','data','spacecraft.csv')
df.to_csv(out_file,header=True)
