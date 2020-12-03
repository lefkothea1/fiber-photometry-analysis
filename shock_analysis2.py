# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 11:47:42 2018

@author: lefko
1sec~230 indexes
1index=0.004125 sec
every 1 index deviation from 230 points/sec = shifted axis values by 0.0002 sec
shock ttl on anIn3 channel of fp


"""

import csv
import pandas as pd
import numpy as np 
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import time



def slash(operating_system):
    if operating_system == 1:
        streep = '//' 
    elif operating_system == 2:
        streep = '/' 
        
    return streep
def split_list(n):  #called only by get_sub_list function
    """takes a list of indices as input,subtracts the next(2) from the previous one(1),and returns the(2nd) index of the pairs that have diference>1"""
    return [(x+1) for x,y in zip(n, n[1:]) if y-x != 1]

def get_sub_list(my_list):
    """will split the list based on the index.returns a list of lists with the individual trials(when shock was ON)in each row"""
    my_index = split_list(my_list)
    output = list()
    prev = 0
    for index in my_index:
        new_list = [ x for x in my_list[prev:] if x < index]
        output.append(new_list)
        prev += len(new_list)
    output.append([ x for x in my_list[prev:]])
    return output
#better names for function inputs; photosignal,indexes to timelock,time before,time after(time before and after are in sample sizes)
def pertrial_array(signal, response, pre_slice,post_slice):
    p=0
    timeindex = np.arange((-pre_slice/230),(post_slice/230), 0.0043478261)
    output = []
    while p < len(response):
        output.append([n for n in signal[(response[p])-pre_slice:(response[p])+post_slice]])
        p += 1
    output = pd.DataFrame(output, dtype='float64')
    output = output.transpose().set_index(timeindex)
    
    return output
        
    #Creates a single avrage array from all the trials 
def arrays_avg(dataframe):
    dataframe['avg'] = dataframe.mean(axis=1, skipna = True)  
    return dataframe 
    
    #Obtains the first index in 'dataframe' which matches the number in 'timearray'
    #creates a list of all the indexes that match the timestamp from 'timearray'.returns the1st?
def get_index(dataframe, timearray):
    output = []
    k =0 
    while k <len(timearray):
        output.append(dataframe.index[(dataframe['Time(s)'] < timearray[k] + 0.01) & (dataframe['Time(s)']  > timearray[k]-0.01)].tolist())
        k+= 1  
    return [x[0] for x in output]


#creates the filde directory for the result to be saved in. inputs: the data directory, in which the saving folder will be created, and an extension for ex: analysis  
def make_path(directory, extension ):
    date = time.strftime('%x'); new_date = date[6:8]; new_date = new_date + date[0:2] ; date = new_date + date[3:5]
    saving_dir = directory + '/'+ str(extension)+'/'+str(date)
    if os.path.exists(saving_dir):
        numbers = [x for x in range(2,100)]
        for i in range(len(numbers)):
            if not os.path.exists(saving_dir + '_' + str(numbers[i])):
                os.makedirs(saving_dir + '_' + str(numbers[i]))
                saving_dir = (saving_dir + '_' + str(numbers[i]))
                break
    else:
        os.makedirs(saving_dir)
    return saving_dir
###########################################################################################################################################################3
#def info_page(filename, saving_dir):
#    firstPage = plt.figure(figsize=(11.69,8.27))
#    firstPage.clf()
#    txt = filename
#    firstPage.text(0.5,0.5,txt, transform=firstPage.transFigure, size=24, ha="center")
##    pp.savefig()
#    plt.savefig(saving_dir+'//'+'infoPage'+".png", bbox_inches='tight') ####change filename WD
#    plt.close()
#
#    

#calculates standard deviation (of sample,NOT population), count, SEM, avg+-sem, for the columns with shock data
def calc_SEM (df, shock_columns):
    
    df['stdev']=df[shock_columns].std(axis=1)
    df['count']=len(shock_columns)
    df['SEM']=df['stdev']/(np.sqrt(df['count']))
    df['avg+sem']=df['avg']+df['SEM']
    df['avg-sem']=df['avg']-df['SEM']
    
    return df
   
    
#creates trials timelocked to each respective event, and their average. takes DF/f0  files(of each event) as input
def make_trials(DFfile):
    
    
    df_photo = pd.read_csv(DFfile, usecols=['Time(s)',"Analog In. | Ch.1 AIn-1 - Dem (AOut-1)_LowPass_dF/F0",'Analog In. | Ch.2 AIn-2 - Dem (AOut-2)_LowPass_dF/F0','Analog In. | Ch.3 AIn-3'] )
    print('start processing'+DFfile[:-8]+'\n')
    
     #checking decimation
    print('in this file has ' + '%.2f' % (230/df_photo.loc[230,'Time(s)']) + ' samples per sec \n')
    
    
    #renames columns
    df_photo = df_photo.rename(columns={'Analog In. | Ch.1 AIn-1 - Dem (AOut-1)_LowPass_dF/F0':'isosb_df/f', 'Analog In. | Ch.2 AIn-2 - Dem (AOut-2)_LowPass_dF/F0': 'gcamp_df/f', 'Analog In. | Ch.3 AIn-3' : "shock"})
    #rounds values (of ttl pulses) for better handling
    df_photo.shock = df_photo.shock.round()
    
    #selects all values (from all columns) during shock and puts them in new dataframe
    shockON= df_photo.loc[df_photo['shock'] >= 1.5]
    
       
    #has ALL the indices from main df_photo, during shocks(whole duration)
    shockIndx = np.array(shockON.index.tolist(), dtype = int)
    #getting the indeces of every first time shock was on.
    indx1stShocks = np.array([x[0] for x in get_sub_list(shockIndx)], dtype = int)
    indx1stShocks=indx1stShocks[:-1]   #drop last value,since pulse always turns on when medpc turns off,at the end of measurment!
    
    #creating a dataframe with the values of all columns(t,df_photo ch1-3).t column is the timestamps for every shock onset.has the original indeces from df_photo
    FirstShockON=df_photo.loc[indx1stShocks]
    
    ShockOnset_TS=FirstShockON['Time(s)'].to_frame().reset_index(drop=True) #making df of ts, ready to be sent to excel
    
     #creates  numpy arrayS of the photosignal of both ch from the dataframe 
    ch1 = np.array(df_photo['isosb_df/f'])
    ch2 = np.array(df_photo['gcamp_df/f'])
        
    #Defines a variable containing the size of the slice of signal you wish to obtain in 'samples' units
    size_before= 690  #3sec
    size_after= 1150  #5sec
    
        
        #creates the trials arrays,with tphotometric data around shock onset using pertrial_array,for each channel 
    photoShock1= pertrial_array(ch1, indx1stShocks, size_before, size_after)
    photoShock2= pertrial_array(ch2, indx1stShocks, size_before, size_after)
    photoShock_mc=photoShock2-photoShock1
    shock_columns=list(photoShock1) #created a list with headers of shock columns. to be used later when df also has avg, sems etc
    
    
        #averages the trials using session_avg 
    photoShock1 = arrays_avg(photoShock1)
    photoShock2 = arrays_avg(photoShock2)
    photoShock_mc=arrays_avg(photoShock_mc)
    
    
    print('trials made for'+str( DFfile[:-7])+ '\n' +'calculating now the SEMs \n')
    
    photoShock1=calc_SEM(photoShock1, shock_columns)
    photoShock2=calc_SEM(photoShock2, shock_columns)
    photoShock_mc=calc_SEM(photoShock_mc, shock_columns)
    
    return photoShock1, photoShock2, ShockOnset_TS, shock_columns, photoShock_mc
    



    #will plot individual trials, already contained in the dataframe. Takes as inputs the df and the event(eg onset-for labeling purposes)&columns to be plotted(trial containing)
def plot_indiv(df,col_to_plot,event, color1, saving_dir ):
    
    print("creating trial plots")    
    
    graph_nr= len (col_to_plot)
    cols = 2
    # Calculates how many Rows are needed, for the given number of total graphs and columns
    rows = graph_nr // cols 
    rows += graph_nr % cols
     # Create a Position index, for placing every subplot
    Position = range(1,graph_nr + 1)
    fig = plt.figure(figsize=(5*cols, 4*rows))
    fig.suptitle(str(event)+ "\n" ,fontsize=15, y=1)  #aadds title over all subplots, y variable for title location
    fig = plt.figure(1)
     # add every single subplot to the figure with a for loop
    for k in range(graph_nr):
        ax = fig.add_subplot(rows,cols,Position[k])
    #selecting lim of y axis from the min/max value from all columns that contain fight data
        ax.set_ylim(df[col_to_plot].min().min(), df[col_to_plot].max().max()) #df.min() gives the min of each column. df.min().min() gives the total min
        x=df.index
        y=df[k]
        ax.plot(x,y,color=color1, label='dF/F0', linewidth=1) 
        ax.set_title ('shock'+str(k))
        plt.axvline(x=0, color='gray',linestyle='dashed', alpha=0.2) 
        plt.xlabel("time (s)")
        plt.ylabel("dF/F0", labelpad=0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
            
    plt.legend()
    plt.tight_layout()
    
#    plt.savefig(saving_dir+"\\"+str(event[5:])+".png", bbox_inches='tight') ####change filename WD
#    pp.savefig()
    plt.show()

#will plot the avg already contained in a dataframe. Inputs: dataframe,columns to be plotted(trial containing),  color, &str of event for labelling
 #adds fig to pdf   
def plot_avg(df,fights_col, event,  color1, saving_dir):
    ax = plt.subplot(111)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tick_params(top=False ,right=False)
    plt.ylabel("dF/F0"); plt.xlabel('Time (s)')
    plt.title("average "+str(event)+"\n", fontsize=15)
    
    #ax.set_ylim(df[fights_col].min().min(), df[fights_col].max().max())# sets the same y axis limits as the individual fights
    
    x=df.index
    y1=df['avg']
    y2=df['avg-sem']
    y3=df['avg+sem']
        
    ax.plot(x,y1 , color=color1, label= 'avg', linewidth=1)
    plt.axvline(x=0, color='gray',linestyle='dashed', alpha=0.2) 

    plt.fill_between(x,y2,y3, color =color1, alpha =0.25)
#    plt.savefig(saving_dir + '\\' + "avg"+event[5:]+".png", bbox_inches='tight')
#    pp.savefig()
    plt.show()      
    

    
def plot_gcampWisosb(df_gcamp,df_isosb,event, gcamp_color, isosb_color):
    ax = plt.subplot(111)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tick_params(top=False ,right=False)
    plt.ylabel("dF/F0"); plt.xlabel('Time (s)')
    plt.title("average "+str(event)+"\n", fontsize=15)
    
    
    x=df_gcamp.index
    y1=df_gcamp['avg']
    y2=df_gcamp['avg+sem']
    y3=df_gcamp['avg-sem']
    
    y4=df_isosb['avg']
    y5=df_isosb['avg+sem']
    y6=df_isosb['avg-sem']
    
        
    ax.plot(x,y1 ,color=gcamp_color, linewidth=1)
    ax.plot(x,y4,color=isosb_color, label='ísosbestic', linewidth=1)
    plt.axvline(x=0, color='gray',linestyle='dashed', alpha=0.2) 


    plt.fill_between(x,y2,y3, color=gcamp_color, alpha =0.25)
    plt.fill_between(x,y5,y6, color=isosb_color, alpha=0.25)
    plt.legend()
#    plt.savefig(dir1 + '\\RESULTS\\' + "avg"+event[5:]+".png", bbox_inches='tight')--> to save every plot as one image
#    pp.savefig()
    plt.show()    
def shock_analysis(filename,directory):
    #creating pdf to save figures and adds first page with mouse info, date, experiment,all in filename
#    
    streep=slash(1)
    photoShock1, photoShock2, shockTS, shock_col,photoShock_mc =make_trials(filename)
#plotting    
    plot_indiv(photoShock2, shock_col, "individual shocks_dLight",'#2ca02c', directory) #gcamp(off)-green
    plot_avg(photoShock2, shock_col, " shock_dLight", '#2ca02c', directory)  
    plot_indiv(photoShock1, shock_col, "individual shocsk_isosb",'#1f77b4', directory) #isosb(off)-blue
    plot_avg(photoShock1, shock_col, " shock_isosb", '#1f77b4', directory)
#    plot_avg(photoShock_mc, shock_col,'shock motion corrected', "#e377c2")# plotss motion corrected signal-BE CAUIOUS
    
#    plot_gcampWisosb(photoShock2,photoShock1, 'shock onset','#2ca02c','#1f77b4')
          
    '''un-comment next block if you need to add plot with adjustable x axis range in plot'''
    #xmin=230 #df starts from -3sec, i want it to start from -2sec, need to drop 1sec, (1*230) not sure if these numbers correct
    #xmax=1150 #x max needed is 2sec, df starts from -3 sec, so need to drop everything after 5 sec (5*230=1150)
    #plot_gcampWisosb(photoShock2.iloc[xmin:xmax],photoShock1[xmin:xmax], 'shock onset','#2ca02c','#1f77b4')
    
    
#    pp.close() #to close the pdf where the plots are saved
    
    
    print('sending data to excel \n')
    
     #Sends the Dataframes to Excel
    writer = pd.ExcelWriter(directory+streep+filename[:-6]+'_RESULT.xlsx')
    photoShock1.to_excel(writer,'shock_isosb', freeze_panes=(1,1) )
    photoShock2.to_excel(writer,'shock_dLight', freeze_panes=(1,1))
    photoShock_mc.to_excel(writer,'motion_corr', freeze_panes=(1,1))
    shockTS.to_excel(writer,'Shock timestamps(sec)',  index_label='shock#')
    writer.save() 
    
#    photoshock_all=pd.concat({'isosb':photoShock1,'gcamp':photoShock2},axis=1) trying to have 1muliindex df with both gcamp &isosb data
    return photoShock1, photoShock2
    print('finished analyzing' +str(filename[:-6]))
    
    
    
 #changes directory to where the files to be read are-use double backslach *********************************************************************************************************************************
dir1 = './data/raw'
os.chdir (dir1)
#saving_dir=make_path(dir1, 'analysis')
saving_dir='./results/output'
streep=slash(1)
batch_avg1=pd.DataFrame() #1 for isosbestic data. will contain the avg of all trials from all mice
batch_avg2=pd.DataFrame() #2 for gcamp data.will contain the avg of all trials from all mice
files=[ '20201110_shock_vglut2cre76-1_lp6hz_DF.csv']
batch_nr='batch_12'
#will loop through the files and create the idividual trials, as well as their average (plot and excel files)
for filename in files:
#    pp = PdfPages(saving_dir+streep+filename[:-6]+'plots.pdf')
#    info_page(filename[:-4], saving_dir)
    photoshock1_pt, photoshock2_pt=(shock_analysis(filename,saving_dir))
