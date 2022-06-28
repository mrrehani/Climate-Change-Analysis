"""
This module creates several patterns to display patterns in how our world's
climate has been changing over the centuries.
"""
import geopandas as gpd
from pandas import DataFrame
import math
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

class Grapher():

  """
  This class implements the temperature_grapher module.
  """
  def graph_map(self, data: DataFrame, century: int,
                row: int, col: int, heat_axs):
    """
    Creates a geographic map of the world,
    using a range of colors to highlight the heatdistribution.

    Keyword arguments:
    data -- The dataframe to use to make the map
    century -- The century in which the data takes place
    row -- Which row of subplots the map should be drawn on
    col -- Which column of subplots the map should be drawn on
    heatAxs -- Which axis to draw the plot on.
    """
    data = data[data["dt"].str.startswith(str(century), na=False)]
    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    for line in data.groupby("Country"):
      country = line[1]["Country"].iloc[0]
      avg_temp = line[1]["AverageTemperature"].mean()
      world.loc[world["name"] == country, "avgTemp"] = avg_temp

    world.plot(column = "avgTemp", edgecolor = "black",
        missing_kwds = {"color": "lightgray", "edgecolor": "black"},
        cmap = "plasma", ax = heat_axs[row, col], legend = True)
    heat_axs[row, col].tick_params(bottom = False, labelbottom = False,
                                  left = False, labelleft = False)
    heat_axs[row, col].set_title(str(century) + "00s",
                                fontdict = {"fontsize":15})

  def group_by_year(self, data: DataFrame, column: str):
    """
    Groups the country data by year

    Keyword arguments:
    data -- The dataframe to group
    column -- Which column to base the grouping on
    """
    year=None
    num_months=0 #This will track how many months of each year has data.
    yearly_average_temp=0
    dict_years={}
    iloc=0
    for entry in data.index: #Iterates through each date.
      iloc+=1
      if year is None:
        year=str(entry)[:4]
        #Adds current year's temperature to the yearly_average_temp variable.
        yearly_average_temp+=data.loc[entry][column]
      elif str(entry)[:4]==year:
        if not math.isnan(data.loc[entry][column]):
          yearly_average_temp+=data.loc[entry][column]
          num_months+=1

      #If the function has encountered a new year
      #or reached the end of the dataframe.
      elif str(entry)[:4]!=year or iloc==len(data):
        #Checking if there were any entries in the current year.
        if num_months !=0:
          dict_years[year]=(yearly_average_temp/num_months)
        yearly_average_temp=0
        #If the first entry of the new year is not NaN,
        #then the temperature will be recorded.
        if not math.isnan(data.loc[entry][column]):
          num_months=1
          yearly_average_temp+=data.loc[entry][column]
        else:
          num_months=0
        year=str(entry)[:4]
    return dict_years


  def graph_change(self, region_names: str, data: DataFrame,
                  temperature_ax, uncertainty_ax, row: int,col: int):
    """
    Graphs the change in temperature/uncertainty over the years.

    Keyword arguments:
    data -- The dict used to make the map
    row -- Which row of subplots the map should be drawn on
    col -- Which column of subplots the map should be drawn on
    tempAx -- Which temperature axis to draw the plot on.
    uncertainAx -- Which uncertainty axis to draw the plot on.
    """
    grouped_data = self.group_by_year(data,"AverageTemperature")
    uncertainty = self.group_by_year(data, "AverageTemperatureUncertainty")
    #The code below creating a linear regression line is from
    #https://realpython.com/linear-regression-in-python/
    #Creating a dataframe from the yearly averages and formatting it properly.
    all_centuries_df=DataFrame([grouped_data])
    all_centuries_df=all_centuries_df.T
    all_centuries_df.reset_index(inplace=True)
    all_centuries_df.columns =["year", "temp"]
    all_centuries_df["uncertainty"]=uncertainty.values()
    #Creating a linear regression line
    x = all_centuries_df["year"].to_numpy().reshape((-1, 1)).astype(int)
    y = all_centuries_df["temp"].to_numpy().astype(float)
    model = LinearRegression().fit(x, y)
    intercept= float(model.intercept_)
    slope=float(model.coef_)
    all_centuries_df["year"]=all_centuries_df["year"].astype("int64")
    #The line of code above is required for the next two lines to work
    #as the years column was previously type str.
    fit = (all_centuries_df["year"] * float(slope)) + float(intercept)
    all_centuries_df["fit"] = fit

    plot_area = all_centuries_df.plot.line(x="year", y="fit",
                                          c="purple",
                                          ax=temperature_ax[row,col])
    #In order to color-code the graph, I need to group the data by the century.

    list_centuries=[]

    for entry in all_centuries_df["year"]:
      #Above I changed the entries in the year column to int.
      #However in order to execute the line below, it needs to be type str
      year=str(entry)

      #Grouping years by century
      list_centuries.append(year[:2]+"00s")

    #Adding an extra column to the dataframe denoting
    #which century each entry is classified into.
    all_centuries_df["century"]=list_centuries
    colors = ["blue", "green", "orange", "red"]
    markers = ["o", "^", "v", ","]
    centuries=set(sorted(list_centuries))
    #The for loop will make a plot for each century in the data set and graph it
    #using the items in the lists "color" and "marker".
    #The loop is from a lecture in the class Data Programming 220 at UW Madison
    for century in centuries:
      #Creating a temporary dataframe containing all entries
      #from the 1700s, 1800s, etc.
      sub_df = all_centuries_df[all_centuries_df["century"]==century]

      #Plotting all data from the current century using
      #the first entry in the color and label list, then removing that entry.
      plot_area = sub_df.plot.scatter(x="year", y="temp",
                                      ax=temperature_ax[row,col],
                                      color=colors.pop(0),
                                      label=century, marker=markers.pop(0))

    plot_area.set_xlabel("Year")
    plot_area.set_ylabel("Temperature")
    title = f"Average Temperatures from the {region_names} Dataset"
    plot_area.set_title(title)

    #Plotting the error margin.
    yerr=[]
    #I am adding the annual average uncertainty entries to a list.
    for entry in  all_centuries_df["uncertainty"]:
      yerr.append(entry)

    #In the expressions x.tolist() and y.tolist(), x and y are are created above
    #when plotting a scatterplot. X is the years columnn of the all_centuries_df
    #dataframe and y is the temperatures.
    uncertainty_ax[row][col].errorbar(x=x, y=y, yerr=yerr, ls="none")
    title = f"Average Uncertainty from the {region_names} Dataset"
    uncertainty_ax[row][col].set_title(title)
    uncertainty_ax[row][col].set_xlabel("Year")
    uncertainty_ax[row][col].set_ylabel("Average Uncertainty")

    #This works properly because yerr, x, and y all come from the same DataFrame
    #Consequently, they will be sorted in the same way
    #and thus line up with each other.


  def group_by_century(self,data: DataFrame, type_place: str):
    """
    Groups the country data by century

    Keyword arguments:
    data -- The dataframe to group
    type_place -- Which type of place is being showcased (e.g. cities, states,
                  countries, etc.)
    """
    curr_place=None
    century_began={1700:[], 1750:[],1800:[], 1850:[],1900:[], 1950:[],2000:[]}
    index=1
    avg_temps=data.groupby(type_place).mean()

    zeroes_replaced = avg_temps["AverageTemperature"].replace(np.nan, 0)
    avg_temps["AverageTemperature"] = zeroes_replaced

    #This loop will figure out the indices of the "dt" column
    #and the place name column.
    for column in data:
      if column=="dt":
        dt_index=index
      elif column==type_place:
        place_index=index
      index+=1
    index=0
    for row in data.itertuples():
      dt,place=row[dt_index],row[place_index]
      #If curr_place==place, then we are not at the place's first entry
      #(when they began recording temperatures).
      #We only need the first entry of each place.
      if curr_place==place:
        continue
      elif curr_place is None or curr_place!=place:
        curr_place=place
        #This will record the year of the first year a place began
        #recording temperatures.
        year_began=int(dt[:4])
      #The conditionals below will classify the place based on when
      #it began recording temperatures.

      #This takes the first two numbers of the yera (which tells us the century)
      #and adds 00 or 50 to it.  E.g. 1846 will become 1800 or 1850.
      temp = [curr_place,index,avg_temps.loc[curr_place]["AverageTemperature"]]
      if int(str(year_began)[2])<5:
        century_began[int(str(year_began)[:2]+"00")].append(temp)
      else:
        century_began[int(str(year_began)[:2]+"50")].append(temp)
      index+=1
    return century_began

  def highest_avg(self,data: DataFrame, type_place: str,
                  row: int, col: int, axs):
    """
    Uses bar plots to showcase which regions of the world where hottest,
    starting at different times.

    Keyword arguments:
    data -- The dataframe to use to make the bar plots
    century -- The century in which the data takes place
    type_place -- Which type of place is being showcased
                  (e.g. cities, states, countries, etc.)
    row -- Which row of subplots the map should be drawn on
    col -- Which column of subplots the map should be drawn on
    axs -- Which axis to draw the plot on.
    """
    century_began = self.group_by_century(data,type_place)
    highest_places,highest_temps=[],[]
    for _, century_list in century_began.items():

      #If no areas began recording temperatures after a specific time period
      #like 2000, the list would be empty.
      if len(century_list)>0:
        #It's fine to hardcode the index of average temperature because
        #the code that creates the list ensures that an average temperature
        #is always recorded.
        sorted_list = sorted(century_list,
                          key = lambda x: int(x[2]),
                          reverse=True)
        #If a place had no recorded temperatures (resulting in the average
        #temperature being NaN), it was replaced with 0.0 in the
        #GroupByCentury function to act as a placeholder of sorts.
        if sorted_list[0][2]>0.0:
          highest_places.append(sorted_list[0][0])
          highest_temps.append(sorted_list[0][2])
    axs[row][col].bar(highest_places, highest_temps,
                      color=["b","r","g","orange","purple","pink","orange"])
    #The code below is from
    #https://stackoverflow.com/questions/57340415/matplotlib-bar-plot-add-legend-from-categories-dataframe-column
    colors = {"1700":"blue", "1750":"red",
              "1800":"green","1850":"orange",
              "1900": "purple", "1950": "pink",
              "2000": "yellow"}
    labels = list(colors.keys())
    handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
    #The code below is from
    #https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot
    plt.legend(handles, labels, loc="center left",
              bbox_to_anchor=(1.05, 1),
              prop={"size": 12.5})
    axs[row][col].set(xlabel=type_place, ylabel="Temperature")
    #This sets the tick locations based on how many entries are in the list.
    axs[row][col].set_xticks(range(len(highest_places)))
    axs[row][col].set_xticklabels(labels=highest_places,rotation=25)
