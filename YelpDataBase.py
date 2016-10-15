import MySQLdb as mdb
import json
import sys
from collections import defaultdict,OrderedDict
import datetime
import re

class Yelpdatabase:
  def __init__(self):
      self.week_day={0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday',6:'Sunday'}
      self.db='wayfarer_incognitech_in'
      self.main_categories=defaultdict(str)
  def createdb(self):
      try:
          # 'ip_address', 'user_name', 'pass_word', 'database_name'
          con = mdb.connect('localhost', 'wayfarrVFCWj0Rh1','Zur5ylN9ISbvXO3','wayfarer_incognitech_in')
          cur = con.cursor()
          cur.execute("create database if not exists %s"%(self.db))

      except mdb.Error, e:
          print "Error in init %d: %s" % (e.args[0],e.args[1])
          sys.exit(1)
      finally:
          if cur: cur.close()
          if con: con.close()

  def user(self,input_file='../yelp_dataset_challenge_academic_dataset/yelp_academic_dataset_user.json',table_name='user'):
      try:
          con = mdb.connect('localhost', 'wayfarrVFCWj0Rh1','Zur5ylN9ISbvXO3','wayfarer_incognitech_in')
          cur = con.cursor()
          cur.execute("use %s"%(self.db))
          cur.execute( 'create table if not exists %s (Id int primary key auto_increment, votes_funny int, votes_useful int, votes_cool int, review_count int,average_stars float, user_id varchar(200), name text)'%(table_name))
          with open(input_file) as f:
             for line in f:
                 tmp=json.loads(line)
                 #print tmp
                 print "insert into %s (votes_funny,votes_useful,votes_cool, review_count, average_stars,user_id, name) values(\"%d\",\"%d\",\"%d\",\"%d\",\"%f\",\"%s\",\"%s\")\n"%(table_name,tmp['votes']['funny'],tmp['votes']['useful'],tmp['votes']['cool'],tmp['review_count'],tmp['average_stars'],tmp['user_id'].encode('utf-8'),tmp['name'].encode('utf-8'))
                 cur.execute("insert into %s (votes_funny,votes_useful,votes_cool, review_count, average_stars,user_id, name) values(\"%d\",\"%d\",\"%d\",\"%d\",\"%f\",\"%s\",\"%s\")\n"%(table_name,tmp['votes']['funny'],tmp['votes']['useful'],tmp['votes']['cool'],tmp['review_count'],tmp['average_stars'],tmp['user_id'].encode('utf-8'),tmp['name'].encode('utf-8')))
      except mdb.Error, e:
          print "Error in creating user %d: %s" % (e.args[0],e.args[1])
          sys.exit(1)
      finally:
          con.commit()
          if cur: cur.close()
          if con: con.close()

  def count_categories(self,categories):
     categories_num=defaultdict(int)
     for item in categories:
       categories_num[item]+=1
     return categories_num

  def business(self,input_file='../yelp_dataset_challenge_academic_dataset/yelp_academic_dataset_business.json',table_name='business'):
      try:
          con = mdb.connect('localhost', 'wayfarrVFCWj0Rh1','Zur5ylN9ISbvXO3','wayfarer_incognitech_in')
          cur = con.cursor()
          cur.execute("use %s"%(self.db))
          cur.execute( 'create table if not exists %s (Id int primary key auto_increment, name text, city text, stars float, review_count int, business_id varchar(200), categories text, longitude float, latitude float)'%(table_name))
          category=[]
          with open(input_file) as f:
             for line in f:
                 tmp=json.loads(line)
                 # append categories
                 [category.append(item) for item in tmp['categories']]
             #count the occurences of each category
             categories_num=self.count_categories(category)
             #print  OrderedDict(sorted(categories_num.items(),key=lambda x: x[1]))

             # loop over again to find the main (most occured) category for each business, this step reduces the no. unique categories from ~500 to 40
          #main_items=[]
          remove_items=['Food'] # remove items from the categories that are too general, eg: food
          with open(input_file) as f:
             for line in f:
                max=0
                main_item=''
                tmp=json.loads(line)
                for item in tmp['categories']:
                   if categories_num[item]>max: #and item not in remove_items:
                      max=categories_num[item]
                      main_item=item
                #print tmp['categories'], main_item
                #main_items.append(main_item)
                print "insert into %s (name,city,stars,review_count,business_id, categories,longitude,latitude) values(\"%s\",\"%s\",\"%f\",\"%d\",\"%s\",\"%s\",\"%f\",\"%f\")\n"%(table_name,tmp['name'].encode('utf-8').replace('"','\\"'),tmp['city'].encode('utf-8'),tmp['stars'],tmp['review_count'],tmp['business_id'].encode('utf-8'),main_item.encode('utf-8'),tmp['longitude'],tmp['latitude'])
                cur.execute("insert into %s (name,city,stars,review_count,business_id, categories,longitude,latitude) values(\"%s\",\"%s\",\"%f\",\"%d\",\"%s\",\"%s\",\"%f\",\"%f\")\n"%(table_name,tmp['name'].encode('utf-8').replace('"','\\"'),tmp['city'].encode('utf-8'),tmp['stars'],tmp['review_count'],tmp['business_id'].encode('utf-8'),main_item.encode('utf-8'),tmp['longitude'],tmp['latitude']))
                # few hacks to merge less frequent categories to bigger categories, before we do that, we keep the 22 categories in business table above, just in case
                if main_item=='Mass Media': main_item='Arts & Entertainment'
                if main_item=='Education' or main_item=='Religious Organizations' or main_item=='Financial Services' or  main_item=='Professional Services' or main_item=='Public Services & Government': main_item='Local Services'
                if main_item=='Local Flavor': main_item='Food'
                if main_item=='': main_item='Other'

                self.main_categories[tmp['business_id']]=main_item
          #print set(self.main_categories.values())
          #print len(list(set(main_items))), list(set(main_items))

          #print len(category),len(list(set(category))),list(set(category))[0:10]

      except mdb.Error, e:
          print "Error in business %d: %s" % (e.args[0],e.args[1])
          sys.exit(1)
      finally:
          con.commit()
          if cur: cur.close()
          if con: con.close()

  def review(self,input_file='../yelp_dataset_challenge_academic_dataset/yelp_academic_dataset_review.json',table_name='review'):
      try:
          con = mdb.connect('localhost', 'wayfarrVFCWj0Rh1','Zur5ylN9ISbvXO3','wayfarer_incognitech_in')
          cur = con.cursor()
          cur.execute("use %s"%(self.db))
          cur.execute( 'create table if not exists %s (Id int primary key auto_increment, votes_funny int, votes_useful int, votes_cool int, user_id varchar(200), review_id varchar(200), business_id varchar(200), stars float, date varchar(100), weekday varchar(30), categories varchar(100), review_text text)'%(table_name))

          with open(input_file) as f:
             for line in f:
                 tmp=json.loads(line)
                 year,month,day=[int(x) for x in tmp['date'].split('-')]
                 print "insert into %s (votes_funny,votes_useful,votes_cool, user_id, review_id, business_id, stars, date, weekday, categories, review_text) values(\"%d\",\"%d\",\"%d\",\"%s\",\"%s\",\"%s\",\"%f\",\"%s\",\"%s\",\"%s\",\"%s\")\n"%(table_name,tmp['votes']['funny'],tmp['votes']['useful'],tmp['votes']['cool'],tmp['user_id'].encode('utf-8'),tmp['review_id'].encode('utf-8'),tmp['business_id'].encode('utf-8'),tmp['stars'],tmp['date'].encode('utf-8'),self.week_day[datetime.date(year, month, day).weekday()].encode('utf-8'), self.main_categories[tmp['business_id'].encode('utf-8')].encode('utf-8'),tmp['text'].encode('utf-8').replace('\\','\\\\').replace('"','\\"'))
                 cur.execute("insert into %s (votes_funny,votes_useful,votes_cool, user_id, review_id, business_id, stars, date, weekday, categories, review_text) values(\"%d\",\"%d\",\"%d\",\"%s\",\"%s\",\"%s\",\"%f\",\"%s\",\"%s\",\"%s\",\"%s\")\n"%(table_name,tmp['votes']['funny'],tmp['votes']['useful'],tmp['votes']['cool'],tmp['user_id'].encode('utf-8'),tmp['review_id'].encode('utf-8'),tmp['business_id'].encode('utf-8'),tmp['stars'],tmp['date'].encode('utf-8'),self.week_day[datetime.date(year, month, day).weekday()].encode('utf-8'), self.main_categories[tmp['business_id'].encode('utf-8')].encode('utf-8'),tmp['text'].encode('utf-8').replace('\\','\\\\').replace('"','\\"')))
      except mdb.Error, e:
          print "Error in review %d: %s" % (e.args[0],e.args[1])
          sys.exit(1)
      finally:
          con.commit()
          if cur: cur.close()
          if con: con.close()

  def checkin(self, input_file='../yelp_dataset_challenge_academic_dataset/yelp_academic_dataset_checkin.json',table_name='checkin'):
     try:
          con = mdb.connect('localhost', 'wayfarrVFCWj0Rh1','Zur5ylN9ISbvXO3','wayfarer_incognitech_in')
          cur = con.cursor()
          cur.execute("use %s"%(self.db))
          cur.execute('create table if not exists %s (Id int primary key auto_increment, business_id varchar(200), weekday varchar(20), checkin_no int, categories varchar(100))'%(table_name))
          with open(input_file) as f:
             for line in f:
                check_in=defaultdict(int)
                tmp= json.loads(line)
                # get the number of checkins per business per day
                # first get all the ckeckins for a business
                d=json.dumps(tmp['checkin_info'],separators=(',',':'),skipkeys=True)
                # add the counts for each day
                for x in d.strip('{}').split(','):
                   l,r= re.split(':+',x)
                   ll,rl=re.split('-',l)
                   check_in[rl.replace('"','')]+=int(r)
                   #print self.week_day[int(rl.replace('"',''))], rl.replace('"','')

                # insert the counts for each day for each entry
                for x in self.week_day.keys():
                       #print x,check_in[str(x)]
                       print "insert into %s (business_id, weekday, checkin_no, categories) values('%s','%s','%d','%s')\n"%(table_name,tmp['business_id'].encode('utf-8'),self.week_day[x].encode('utf-8'),check_in[str(x)],self.main_categories[tmp['business_id'].encode('utf-8')])
                       cur.execute("insert into %s (business_id, weekday, checkin_no, categories) values('%s','%s','%d','%s')\n"%(table_name,tmp['business_id'].encode('utf-8'),self.week_day[x].encode('utf-8'),check_in[str(x)],self.main_categories[tmp['business_id'].encode('utf-8')]))
     except mdb.Error, e:
          print "Error in checkin %d: %s" % (e.args[0],e.args[1])
          sys.exit(1)
     finally:
          con.commit()
          if cur: cur.close()
          if con: con.close()

if __name__ == "__main__":
   ydb=Yelpdatabase()
   #ydb.createdb()
#   ydb.user()
#   ydb.business()
   ydb.review()
#   ydb.checkin()
