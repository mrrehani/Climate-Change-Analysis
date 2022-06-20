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
    def graph_data(self, data, dataColumn, uncertainty,uncertaintyColumn, type_data):    
        data, uncertainty = self.group_by_year(data,dataColumn), self.group_by_year(uncertainty, uncertaintyColumn)
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
        #This works properly because yerr, x, and y allcome from the same DataFrame. Consequently, they will be sorted in the same way and thus line up with each other.
