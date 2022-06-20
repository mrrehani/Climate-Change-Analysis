import pandas as pd
import geopandas as gpd
from pandas import DataFrame
import math
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
class TemperatureGrapher():
    #This function groups the country data by year
    def group_by_year(self, DF, column):  
        year=None
        num_months=0  #This will track how many months of each year has data. 
        yearly_average_temp=0
        dict_years={}
        iloc=0
        for entry in DF.index: #Iterates through each date.
            iloc+=1
            if year==None:
                year=str(entry)[:4] 
                yearly_average_temp+=DF.loc[entry][column] #Adds current year's temperature to the yearly_average_temp variable.
            elif str(entry)[:4]==year:
                if not math.isnan(DF.loc[entry][column]): 
                    yearly_average_temp+=DF.loc[entry][column]
                    num_months+=1     
            elif str(entry)[:4]!=year or iloc==len(DF): #If the function has encountered a new year or reached the end of the dataframe. 
                if num_months !=0: #This checks if there were any entries in the current year. 
                    dict_years[year]=(yearly_average_temp/num_months) #Records the average temperature of the current year.
                yearly_average_temp=0 
                if not math.isnan(DF.loc[entry][column]): #If the first entry of the new year is not NaN, then the temperature will be recorded.
                    num_months=1
                    yearly_average_temp+=DF.loc[entry][column]
                else:
                    num_months=0
                year=str(entry)[:4]
        return (dict_years)


    def graph_data(self, data, dataColumn,uncertaintyColumn, type_data):    
        data, uncertainty = self.group_by_year(data,dataColumn), self.group_by_year(data, uncertaintyColumn)
        #The code below creating a linear regression line is from https://realpython.com/linear-regression-in-python/
        #Creating a dataframe from the yearly averages and formatting it properly. 
        all_centuries_df=DataFrame([data]) #Data is a dict of the average temperature each year.
        all_centuries_df=all_centuries_df.T
        all_centuries_df.reset_index(inplace=True)
        all_centuries_df.columns =['year', 'temp'] 
        all_centuries_df["uncertainty"]=uncertainty.values()
        #Creating a linear regression line
        x = all_centuries_df["year"].to_numpy().reshape((-1, 1)).astype(int) #Turns the 1D array of years into a 2D array
        y = all_centuries_df["temp"].to_numpy().astype(float)
        model = LinearRegression().fit(x, y)
        r_sq=model.score(x, y)#Returns r^2 
        intercept= float(model.intercept_)
        slope=float(model.coef_)
        all_centuries_df["year"]=all_centuries_df["year"].astype("int64")#Setting the years column to type int. 
        #The line of code above is required for the next line to work, as the years column was previously type str.
        all_centuries_df["fit"] = (all_centuries_df["year"] * float(slope)) + float(intercept)#Obtains y values through the formula y=mx+b.
        fig, axs = plt.subplots(2,1,figsize=(7.5,7.5)) 
        plt.subplots_adjust(hspace=.33)
        plot_area=all_centuries_df.plot.line(x='year', y='fit', c='purple', ax=axs[0])
        #In order to color-code the graph, I need to group the data by the century.
        list_centuries=[]
        for entry in all_centuries_df["year"]:
            year=str(entry) #Above I changed the entries in the year column to int. However in order to execute the line below
            #it needs to be type str
            list_centuries.append(year[:2]+"00s") #This way, entries from the years 1752 1713 1763 1794 will all be grouped as "1700s" (for example).
        all_centuries_df["century"]=list_centuries #Adds an extra column to the dataframe denoting which century each entry is classified into.
        colors = ["blue", "green", "orange", "red"]
        markers = ["o", "^", "v", ","]
        centuries=set(sorted(list_centuries))
        #The for loop will make a plot for each century in the data set and graph it using the items in the lists "color" and "marker".
        #The loop is copied from a lecture in the class Data Programming 220 at UW Madison
        for variety in centuries: #variety is each century, so it is '1700s', '1800s', etc.
            sub_df = all_centuries_df[all_centuries_df["century"]==variety] #Creating a temporary dataframe containing all entries from the 1700s, then the 1800s, etc. 
            plot_area = sub_df.plot.scatter(x="year", y="temp",ax=axs[0], #Plots all data from the current century using the first entry in the color and label list, then removing that entry. 
                                            color=colors.pop(0),
                                            label=variety, marker=markers.pop(0)) 

        plot_area.set_xlabel("Year")
        plot_area.set_ylabel("Temperature")
        plot_area.set_title("Change in Average Temperature Each Year")
        #Plotting the error margin. 
        yerr=[]
        #I am adding the annual average uncertainty entries to a list. 
        for entry in  all_centuries_df["uncertainty"]:
            yerr.append(entry)
        fig = plt.figure()
        #In the expressions x.tolist() and y.tolist(), x and y are are created above when plotting a scatterplot. X is the years columnn of the all_centuries_df dataframe and y is the temperatures.
        x_axis=x.tolist() 
        y_axis=y.tolist()
        axs[1].errorbar(x=x, y=y, yerr=yerr, ls='none') #Plotting the errorbar onto the second subplot at the second row.
        axs[1].set_title("Average Uncertainty Each Year")
        axs[1].set_xlabel("Year")
        axs[1].set_ylabel("Average Uncertainty")
        plt.show()
        print("The coefficient of determination is", r_sq)
        print ("The data above is from the", type_data,"data set.")
        #This works properly because yerr, x, and y all come from the same DataFrame. Consequently, they will be sorted in the same way and thus line up with each other.


    def group_by_century(self,df, type_place):
        curr_place=None
        century_began={1700:[], 1750:[],1800:[], 1850:[],1900:[], 1950:[],2000:[]} #Each place will be placed in a list depending on when it began recording temperatures.
        index=1
        avg_temps=df.groupby(type_place).mean()
        avg_temps['AverageTemperature'] = avg_temps['AverageTemperature'].replace(np.nan, 0)
        for column in df: #This loop will figure out the indeces of the "dt" column and the place name column. 
            if column=="dt":
                dt_index=index
            elif column==type_place:
                place_index=index
            index+=1
        index=0
        for row in df.itertuples(): #This will iterate through each entry in the data frame. 
            dt,place=row[dt_index],row[place_index]
            if curr_place==place: #If curr_place==place, then we are not at the place's first entry (when they began recording temperatures). We only need the first entry of each place.
                continue
            elif curr_place==None or curr_place!=place: 
                curr_place=place
                year_began=int(dt[:4])#This will record the year of the first year a place began recording temperatures.
            #The conditionals below will classify the place based on when it began recording temperatures.
            if int(str(year_began)[2])<5:#If the third number of the year is less than 5 (e.g. 1846 4<5).
                century_began[int(str(year_began)[:2]+"00")].append([curr_place,index,avg_temps.loc[curr_place]["AverageTemperature"]])#This takes the first two numbers of the yera (which tells us the century) and adds 00 to it. It needs to temporarily be a string to concatonate the two. E.g. 1846 will become 1800.
            else:
                century_began[int(str(year_began)[:2]+"50")].append([curr_place,index,avg_temps.loc[curr_place]["AverageTemperature"]])
            index+=1
        return century_began

    def highest_avg(self,df, type_place, row, col, axs):
        century_began = self.group_by_century(df,type_place)
        highest_places,highest_temps=[],[]
        for century in century_began:
            if len(century_began[century])>0:#If no areas began recording temperatures after a specific time period like 2000, the list would be empty.
                sorted_list=sorted(century_began[century], key = lambda x: int(x[2]), reverse=True) #Sorts the list by average temperature. It's fine to hardcode the index of average temperature because the code that creates the list ensures that an average temperature is always recorded.
                #If a place had no recorded temperatures (resulting in the average temperature being NaN), it was replaced with 0.0 in the group_by_century function to act as a placeholder of sorts. 
                if sorted_list[0][2]>0.0: 
                    highest_places.append(sorted_list[0][0])
                    highest_temps.append(sorted_list[0][2])
        
        bar_top_temps = axs[row][col].bar(highest_places, highest_temps, color=['b','r','g','orange','purple','pink','orange'])
        #The code below is from https://stackoverflow.com/questions/57340415/matplotlib-bar-plot-add-legend-from-categories-dataframe-column
        colors = {'1700':'blue', '1750':'red', '1800':'green','1850':'orange', '1900': 'purple', '1950': 'pink', '2000': "yellow"}         
        labels = list(colors.keys())
        handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
        #The code below is from https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot
        plt.legend(handles, labels, loc='center left', bbox_to_anchor=(1.05, 1),prop={'size': 12.5})
        axs[row][col].set(xlabel=type_place, ylabel='Temperature')
        axs[row][col].set_xticks(range(len(highest_places))) #This sets the tick locations based on how many entries are in the list.
        axs[row][col].set_xticklabels(labels=highest_places,rotation=25)
