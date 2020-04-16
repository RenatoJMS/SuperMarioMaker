#!/usr/bin/env python
# coding: utf-8

# In[4]:


'''IS THERE A RELATION BETWEEN HUGE WORLD RECORDS 
    AND LEVEL DIFFICULTY ON SUPER MARIO MAKER??'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.api.types import CategoricalDtype

#First, we read and clean the records table
records=pd.read_csv('records.csv')
aux1=records['catch\tid\tplayer\ttimeRecord']
recarray=np.array([str.split(aux1[i],'\t') for i in range(0,len(aux1))])
recdf=pd.DataFrame({'Date':recarray[:,0],'Level ID':recarray[:,1],'Fastest Player ID':recarray[:,2],
                    'Record':recarray[:,3]}).astype({'Record':'float64'})

#We also want to do this to the the courses table. This table returns a bizarre error, 
#which we fix with "error_bad_lines=False"
courses=pd.read_csv('courses.csv', error_bad_lines=False)
aux2=courses['id\tdifficulty\tgameStyle\tmaker\ttitle\tthumbnail\timage\tcreation']
coarray=np.array([str.split(aux2[i],'\t') for i in range(0,len(aux2))])
cdf=pd.DataFrame({'Level ID':coarray[:,0],'Difficulty':coarray[:,1],'Style':coarray[:,2],
                  'Maker ID':coarray[:,3],'Title':coarray[:,4], 'Thumbnail':coarray[:,5],
                  'Image':coarray[:,6],'Creation':coarray[:,7]}).drop({'Thumbnail','Image'},axis=1)

#Now we join both tables and order by time record:
courses_and_records=pd.merge(cdf, recdf, how='left', left_on='Level ID', 
                             right_on='Level ID').sort_values(by='Record', ascending=False)

#Lets see the courses with more than 20min of world record and the courses with less than 5 min of world record:
grind=courses_and_records[courses_and_records['Record']>1200000]
low=courses_and_records[courses_and_records['Record']<=300000]
#Remember that in Super Mario Maker there are only 4 difficulty levels
easy=grind[grind['Difficulty']=='easy']
normal=grind[grind['Difficulty']=='normal']
expert=grind[grind['Difficulty']=='expert']
superexpert=grind[grind['Difficulty']=='superExpert']
print('There are',len(superexpert['Level ID']),' Super Expert levels, ',
      len(expert['Level ID']),' Expert levels, ',len(normal['Level ID']),' Normal levels and ',
      len(easy['Level ID']),' Easy levels with a grinding time >20 min')

low['Difficulty'].astype(CategoricalDtype(categories=['easy','normal','expert','superExpert'],ordered=True))
low=low.sort_values(by=['Difficulty','Record'], ascending=True)
names=[i for i in range(0,len(low['Record']))]
plt.bar(names,low['Record'])
plt.ylabel('World Record')
plt.xlabel('Levels by difficulty: Easy< Normal < Expert < Super Expert')
plt.show()


# In[12]:


'''IS THERE A RELATION BETWEEN CLEAR RATE AND DIFFICULTY?'''

import pandas as pd
import numpy as np

#Let's read and adjust the courses table:
courses=pd.read_csv('courses.csv', error_bad_lines=False)
aux2=courses['id\tdifficulty\tgameStyle\tmaker\ttitle\tthumbnail\timage\tcreation']
coarray=np.array([str.split(aux2[i],'\t') for i in range(0,len(aux2))])
cdf=pd.DataFrame({'Level ID':coarray[:,0],'Difficulty':coarray[:,1],'Style':coarray[:,2],
                  'Maker ID':coarray[:,3],'Title':coarray[:,4], 'Thumbnail':coarray[:,5],
                  'Image':coarray[:,6],'Creation':coarray[:,7]}).drop({'Thumbnail','Image'},axis=1)

#In order to relate clear rate to other stuff, we need the meta table:
meta=pd.read_csv('course-meta.csv')
aux3=meta['catch\tid\tfirstClear\ttag\tstars\tplayers\ttweets\tclears\tattempts\tclearRate']
metarray=np.array([str.split(aux3[i],'\t') for i in range(0,len(aux3))])
mdf=pd.DataFrame({'Date':metarray[:,0],'Level ID':metarray[:,1],'First Clear':metarray[:,2],
                  'Tag':metarray[:,3],'Stars':metarray[:,4], '# Players who played':metarray[:,5],
                  'Tweets':metarray[:,6],'# Clears':metarray[:,7],'# Attempts':metarray[:,8],
                 'Clear Rate':metarray[:,9]}).drop({'Tweets','Date','Tag'},axis=1).astype({'# Players who played': 'int32',
                                                                                           '# Clears': 'int32', '# Attempts': 'int32',
                                                                                           'Clear Rate': 'float64', 'Stars':'int32'})

#The meta table takes in account temporal changes. We'll fix this:
fixmdf=mdf.groupby('Level ID').agg({'# Players who played': np.amax,'# Attempts':np.amax, 
                                    '# Clears':np.amax}).reset_index()
fixmdf['Clear Rate']=[fixmdf['# Clears'][i]/fixmdf['# Attempts'][i] for i in range(0,115032)]

#Joining tables and ordering by clear rate:
meta_and_courses=pd.merge(cdf,fixmdf, how='left', left_on='Level ID',
                          right_on='Level ID').sort_values(by='Clear Rate', ascending=True)

#Setting a clear rate of <5% as low, we finally have:
low_clear=meta_and_courses[meta_and_courses['Clear Rate']<0.05]
easy=low_clear[low_clear['Difficulty']=='easy']
normal=low_clear[low_clear['Difficulty']=='normal']
expert=low_clear[low_clear['Difficulty']=='expert']
superexpert=low_clear[low_clear['Difficulty']=='superExpert']

print('There are',len(superexpert['Level ID']),' Super Expert levels, ',
      len(expert['Level ID']),' Expert levels, ',len(normal['Level ID']),' Normal levels and ',
      len(easy['Level ID']),' Easy levels with a clear rate < 0.05 \nThere are',superexpert['# Attempts'].sum(),' Super Expert attempts ',
      expert['# Attempts'].sum(),' Expert attempts, ',normal['# Attempts'].sum(),' Normal attempts and ',
      easy['# Attempts'].sum(),' Easy attempts \nThere are',superexpert['# Players who played'].sum(),' players who played Super Expert courses*',
      expert['# Players who played'].sum(),' players who played Expert courses* , ',normal['# Players who played'].sum(),' players who played Normal courses* and ', 
      easy['# Players who played'].sum(),'players who played Easy courses* \n*With <5% clear rate.')


# In[5]:


'''CORRELATION TESTS FOR META TABLE'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.api.types import CategoricalDtype

#Let's read and adjust the courses table:
courses=pd.read_csv('courses.csv', error_bad_lines=False)
aux2=courses['id\tdifficulty\tgameStyle\tmaker\ttitle\tthumbnail\timage\tcreation']
coarray=np.array([str.split(aux2[i],'\t') for i in range(0,len(aux2))])
cdf=pd.DataFrame({'Level ID':coarray[:,0],'Difficulty':coarray[:,1],'Style':coarray[:,2],
                  'Maker ID':coarray[:,3],'Title':coarray[:,4], 'Thumbnail':coarray[:,5],
                  'Image':coarray[:,6],'Creation':coarray[:,7]}).drop({'Thumbnail','Image'},axis=1)

#In order to relate clear rate to other stuff, we need the meta table:
meta=pd.read_csv('course-meta.csv')
aux3=meta['catch\tid\tfirstClear\ttag\tstars\tplayers\ttweets\tclears\tattempts\tclearRate']
metarray=np.array([str.split(aux3[i],'\t') for i in range(0,len(aux3))])
mdf=pd.DataFrame({'Date':metarray[:,0],'Level ID':metarray[:,1],'First Clear':metarray[:,2],
                  'Tag':metarray[:,3],'Stars':metarray[:,4], '# Players who played':metarray[:,5],
                  'Tweets':metarray[:,6],'# Clears':metarray[:,7],'# Attempts':metarray[:,8],
                 'Clear Rate':metarray[:,9]}).drop({'Tweets','Date','Tag'},axis=1).astype({'# Players who played': 'int32',
                                                                                           '# Clears': 'int32', '# Attempts': 'int32',
                                                                                           'Clear Rate': 'float64', 'Stars':'int32'})

#The meta table takes in account temporal changes. We'll fix this:
fixmdf=mdf.groupby('Level ID').agg({'# Players who played': np.amax,'# Attempts':np.amax, 
                                    '# Clears':np.amax}).reset_index()
fixmdf['Clear Rate']=[fixmdf['# Clears'][i]/fixmdf['# Attempts'][i] for i in range(0,115032)]

#Joining tables and ordering by difficulty::
meta_and_courses=pd.merge(cdf,fixmdf, how='left', left_on='Level ID',
                          right_on='Level ID')
meta_and_courses['Difficulty'].astype(CategoricalDtype(categories=['easy','normal','expert','superExpert'],ordered=True))
meta_and_courses=meta_and_courses.sort_values(by=['Difficulty','Clear Rate'], ascending=True)
names=[i for i in range(0,len(meta_and_courses['Clear Rate']))]
plt.bar(names,meta_and_courses['Clear Rate'])
plt.ylabel('Clear Rate')
plt.xlabel('Courses by Difficulty: From Easy to Super Expert')
plt.show()
meta_and_courses


# In[ ]:




