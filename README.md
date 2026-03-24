# Exercise: Analyzing NYC Traffic Accidents

## Summary

This exercise analyzes traffic accident data from New York City's [Vision Zero Open Data Site](https://www.nyc.gov/content/visionzero/pages/open-data). Vision Zero is NYC's plan for eliminating serious injuries and fatalities from motor vehicle accidents. The exercises examines patterns in accidents and fatalities across boroughs and over time. It uses SQL queries to extract data from a SQLite database, and then analyzes the results using Pandas and a range of Seaborn plots including `displot` and `clustermap`.

## Input Data

The input data is a SQLite database file called **nyc-crashes.db** that will need to be downloaded from the course Google Drive folder. It was built from data obtained from the Vision Zero site but has been tidied up a bit and trimmed down to complete years that use the city's current recording methodology. It has three main tables:

The **crash** table contains one record for each collision. Key fields include `collision_id`, which uniquely identifies each crash, `borough`, which indicates where the crash occurred (Manhattan, Brooklyn, Queens, Bronx, or Staten Island), and `year`, which gives the year the crash occurred. It also contains street names, zip codes, geographic coordinates, and the time of the accident, although those will not be used in this assignment.

The **person** table contains information about people involved in crashes, including victims and drivers. Key fields include `collision_id`, which links to the crash table, `person_type`, which indicates whether the person was a pedestrian, cyclist, motorist, or other type, `person_injury`, which indicates the severity of injury (including "Killed" for fatalities), `person_role`, which indicates whether the person was a driver, passenger, or pedestrian, `person_age`, which gives the person's age, `ped_action`, which describes what a pedestrian was doing at the time of the crash (crossing, not crossing, etc.), and `vehicle_id` which contains contains the `unique_id` of a vehicle in the `vehicle` table if the individual was in a vehicle at the time of the crash.

The **vehicle** table contains information about vehicles involved in crashes. Key fields include `collision_id`, which links to the crash table, `unique_id`, which identifies the specific vehicle, `vehicle_type`, which describes the type of vehicle (sedan, SUV, truck, etc.), `pre_crash`, which describes what the vehicle was doing immediately before the crash (going straight, turning, backing up, etc.), and `driver_license_status`, which indicates the status of the driver's license.

There is also a smaller sample database called **nyc-crashes-sample.db** that you can use for testing your code. It contains a subset of the full data and will run much faster. CSV files with sample records from the three databases are available as well. Finally, there is a database called **demo.db** that is used by the demo script.

## Deliverables

A script called **assess.py** that extracts data from the database, performs analyses, and produces twelve figures examining various aspects of traffic crashes and fatalities. The script will also produce three CSV files (`fatal.csv`, `ped.csv`, and `veh.csv`) containing intermediate results.

## Instructions

Please prepare a script called `assess.py` as described below. The script will make heavy use of SQL queries to extract data from the database and then use Pandas and Seaborn to analyze the results.

### A. Initial setup and helper functions

1. Import `pandas` as `pd`, `sqlite3`, `seaborn` as `sns`, and `matplotlib.pyplot` as `plt`.

1. Set the default resolution of plots to 300.

1. Set the Pandas option `pd.options.mode.copy_on_write` to `True`.

1. Define a function called `stdfig()` that takes two arguments, `data` (hint `pd.DataFrame`) and `title` (hint `str`). The function will be used to draw standardized bar graphs showing counts by borough and year. The function should do the following:

    1. Set the `"borough"` column of `data` equal to the result of calling the `.str.title()` method on `data["borough"]`. This will capitalize the first letter of each borough name.

    1. Set `fig,ax` equal to the result of calling `plt.subplots()`.

    1. Set the figure title by calling `.suptitle()` on `fig` with argument `title`.

    1. Draw a bar plot by calling `sns.barplot()` with five arguments: `data=data`, `x="borough"`, `y="count"`, `hue="year"`, `ax=ax`, and `palette="tab10"`. The `hue` argument tells Seaborn to use different colors for different years, and `palette="tab10"` specifies which color scheme to use.

    1. Turn off the X axis label by calling `.set_xlabel()` on `ax` with argument `""` (an empty string) and turn off the Y axis label by calling `.set_ylabel()` on `ax` with argument `""`.

    1. Format the Y axis to use comma separators by calling `.set_major_formatter()` on `ax.yaxis` with the argument `"{x:,.0f}"`. This is a format string that tells Matplotlib to format numbers with commas and no decimal places. The `x` is a placeholder for the number. Note that this is an ordinary string, *not* an f-string and should *not* be preceded by an `f`.

    1. Position the legend by calling `.legend()` on `ax` with arguments `loc="upper left"` and `bbox_to_anchor=(1,1)`. This places the legend just outside the upper right corner of the plot.

    1. Finalize the layout by calling `.tight_layout()` on `fig`.

    1. Return `fig`.

1. Define a function called `topcats()` that takes two required arguments and one optional argument: `var` (hint `pd.Series`), `title` (hint `str`), and `limit` (hint `int|None` with a default value of `None`). The function will be used to draw bar graphs of the most common categories in a variable. The function should do the following:

    1. Set `kinds` equal to the result of calling the `.value_counts()` method on `var`. This will count how many times each unique value appears in the series.

    1. Check whether the number of categories should be limited by starting an `if` block that tests whether `limit is not None and limit < len(kinds)`. If the test is true, do the following within the block:

        1. Set `fold_kinds` equal to the result of using `kinds[limit:]` to select all the categories beyond the limit and then using `.index` to get just their names.

        1. Set `var` equal to the result of calling the `.mask()` method on `var` with two arguments: `var.isin(fold_kinds)` and `"Other"`. This replaces all the categories beyond the limit with the string "Other".

        1. Update the title by setting `title` equal to an f-string: `f"{limit} Most Common {title}"`.

        1. Recalculate the value counts by setting `kinds` equal to the result of calling `.value_counts()` on the updated `var`.

    1. After the `if` block, set `fig,ax` equal to the result of calling `plt.subplots()`.

    1. Set the figure title by calling `.suptitle()` on `fig` with argument `title`.

    1. Draw a horizontal bar graph by calling the `.plot.barh()` method on `kinds` with argument `ax=ax`.

    1. Turn off the Y axis label by calling `.set_ylabel()` on `ax` with argument `""`. Then set the X axis label by calling `.set_xlabel()` on `ax` with argument `"Count"`.

    1. Finalize the layout by calling `.tight_layout()` on `fig`.

    1. Return `fig`.

### B. Connecting to the database and analyzing accidents

1. Set variable `dbname` equal to the string `"nyc-crashes.db"`. When testing your code, you may want to use `"nyc-crashes-sample.db"` instead since it will run much faster.

1. Create a connection to the database by setting `con` equal to the result of calling `sqlite3.connect()` with argument `dbname`.

1. Now we'll extract data on the number of accidents by borough and year. Create a variable called `sql` from the following information. It should be a single multi-line string enclosed in triple quotes.

    * Select `borough`, `year`, `COUNT(*)` `AS` `count`

    * From `crash`

    * Group by `borough`, `year`

    This query groups the crash records by borough and year and counts the number of crashes in each group.

1. Execute the query and load the results into a dataframe by setting `res` equal to the result of calling `pd.read_sql()` with arguments `sql` and `con`.

1. Create a figure by setting `fig` equal to the result of calling `stdfig()` with arguments `res` and `"Accidents by Borough and Year"`.

1. Save the figure by calling `.savefig()` on `fig` with argument `"fig1.png"`.

### C. Analyzing fatalities

1. Now we'll look at fatalities by borough, year, and type of victim. Set `sql` equal a triple-quoted multi-line string using the following:

    * Select `person_type`, `borough`, `year`, `COUNT(*)` `AS` `count`

    * From `person` joined to `crash` using `collision_id`

    * Where `person_injury = 'Killed'`

    * Group by `person_type`, `borough` , `year`

    This query joins the person and crash tables, filters for people who were killed, and counts fatalities by victim type, borough, and year.

1. Set `fatal` equal to the result of calling `pd.read_sql()` with arguments `sql` and `con`.

1. Write the fatality data to a CSV file by calling `.to_csv()` on `fatal` with arguments `"fatal.csv"` and `index=False`.

1. Compute total fatalities by borough and year (summing across victim types) by setting `total` equal to the result of calling `.sum()` on `fatal` grouped by `["borough","year"]` for column `"count"`. That is, use `.groupby()` on `fatal` to group by borough and year, select the `"count"` column, and call `.sum()`.

1. Reset the index by setting `total` equal to the result of calling `.reset_index()` on `total`. This converts the grouped result back into a regular dataframe.

1. Create a figure by setting `fig` equal to the result of calling `stdfig()` with arguments `total` and `"Fatalities by Borough and Year"`.

1. Save the figure by calling `.savefig()` on `fig` with argument `"fig2.png"`.

### D. Breaking down fatalities by victim type

1. Set the `"borough"` column of `fatal` equal to the result of calling `.str.title()` on `fatal["borough"]` to capitalize borough names.

1. Set `fig,ax` equal to the result of calling `plt.subplots()`.

1. Set the figure title by calling `.suptitle()` on `fig` with argument `"Mean Annual Fatalities by Type of Victim"`.

1. Draw a bar plot by calling `sns.barplot()` with five arguments: `data=fatal`, `x="borough"`, `y="count"`, `hue="person_type"`, and `ax=ax`.

1. Position the legend by calling `.legend()` on `ax` with five arguments: `ncols=4`, `loc="lower center"`, `bbox_to_anchor=(0.5,1)`, `fontsize="small"`, and `frameon=False`. This places the legend horizontally above the plot with 4 columns and turns off a frame around it.

1. Turn off both axis labels by calling `.set_xlabel()` and `.set_ylabel()` on `ax` with empty strings as arguments.

1. Finalize the layout by calling `.tight_layout()` on `fig`.

1. Save the figure by calling `.savefig()` on `fig` with argument `"fig3.png"`.

### E. Focusing on pedestrian fatalities

1. Filter the data to pedestrian fatalities only by setting `peds` equal to the result of calling the `.query()` method on `fatal` with argument `"person_type == 'Pedestrian'"`.

1. Create a figure by setting `fig` equal to the result of calling `stdfig()` with arguments `peds` and `"Pedestrian Fatalities by Borough and Year"`.

1. Save the figure by calling `.savefig()` on `fig` with argument `"fig4.png"`.

### F. Detailed analysis of pedestrian victims

1. Now we'll get detailed information about pedestrian fatalities. Set `sql` equal to a triple-quoted
string built from the following information:

    * Select `collision_id`, `CAST(person_age AS INTEGER)` `AS` `age`, `ped_action` `AS` `action`

    * From `person`

    * Where `person_injury = 'Killed'` and `person_type = 'Pedestrian'`

    The `CAST()` function converts the age field from text to an integer.

1. Set `ped` equal to the result of calling `pd.read_sql()` with arguments `sql` and `con`.

1. Write the data to a CSV file by calling `.to_csv()` on `ped` with arguments `"ped.csv"` and `index=False`.

1. Create a histogram of pedestrian ages by setting `fg` equal to the result of calling `sns.displot()` with three arguments: `ped`, `x="age"`, `kind="hist"`, and `kde=True`.

1. Set the figure title by calling `.suptitle()` on `fg.figure` with argument `"Ages of Pedestrians Killed"`.

1. Set the axis labels by calling `.set_axis_labels()` on `fg` with arguments `"Age"` and `"Number"`.

1. Finalize the layout by calling `.tight_layout()` on `fg`.

1. Save the figure by calling `.savefig()` on `fg` with argument `"fig5.png"`.

1. Create a figure showing pedestrian actions by setting `fig` equal to the result of calling `topcats()` with three arguments: `ped["action"]`, `"Pedestrian Actions"`, and `limit=10`.

1. Save the figure by calling `.savefig()` on `fig` with argument `"fig6.png"`.

### G. Examining the age and actions of the pedestrians

1. Remove records with missing age or action data by setting `ped_trim` equal to the result of calling `.dropna()` on `ped` with argument `subset=["age","action"]`.

1. Create age bins by setting a new column `"age_bin"` in `ped_trim` equal to `10*(ped_trim["age"]//10)`. This groups ages into decades (0-9, 10-19, 20-29, etc.). The `//` operator is integer division, which drops anything after the decimal point.

1. Set `grid` equal to the result of calling `.size()` on `ped_trim` grouped by `["age_bin","action"]`. This counts how many people in each age bin were doing each action.

1. Reshape the data by setting `grid` equal to the result of calling `.unstack()` on `grid` with argument `"age_bin"` and then calling `.fillna(0)` on the result. Note that the cells with missing data before the call to `.fillna()` were combinations of ages and actions that were never observed, so those counts are legitimately 0 rather than missing.

1. Improve the column labels by setting `grid.columns` equal to the result of using a list comprehension: `[f"{g:.0f}s" for g in grid.columns]`. This formats each age bin as "10s", "20s", "30s", etc.

1. Create a clustered heatmap by setting `cg` equal to the result of calling `sns.clustermap()` with two arguments: `grid` and `annot=True`. The `annot=True` argument displays the counts in each cell.

1. Set the X axis label by calling `.set_xlabel()` on `cg.ax_heatmap` with argument `"Age Range"`. and set the Y axis label by calling `.set_ylabel()` on `cg.ax_heatmap` with argument `"Pedestrian Action"`.

1. Save the figure by calling `.savefig()` on `cg` with argument `"fig7.png"`.

### H. Analyzing vehicles involved in fatal pedestrian crashes

1. Now we'll get information about vehicles involved in crashes where pedestrians were killed. This will involve a complex query so we'll break it down into three separate strings and spell two of them out explicitly. Ordinarily, this would be done with one long string.

    1. Set `sql_select` equal to a SQL string that selects `collision_id`, `vehicle_type` `AS` `type`, `pre_crash`, `driver_license_status` `AS` `license`, and `CAST(person_age AS INTEGER)` `AS` `driver_age`. It will be best to do this as a triple-quoted multi-line string.

    1. Then set `sql_from` to the following multi-line string:

        ```python
        sql_from = """
            FROM
                vehicle
                LEFT JOIN (
                    SELECT
                        collision_id,
                        vehicle_id AS unique_id,
                        person_age
                    FROM
                        person
                    WHERE
                        person_role = 'Driver'
                    )
                USING (collision_id,unique_id)
        """
        ```

        This uses a subquery within the join clause to add driver information to vehicle records when it is available. The `LEFT` is important because otherwise vehicles without driver information would be dropped. Since the NYC database uses `vehicle_id` in the `person` table to link to the vehicle's `unique_id` in the `vehicle` table, the subquery renames `vehicle_id` to make it easy to match the records with the `USING` clause.

    1. Finally, set `sql_where` to the following string:

        ```python
        sql_where = """
            WHERE
                collision_id IN (
                    SELECT
                        collision_id
                    FROM
                        person
                    WHERE
                        person_type = 'Pedestrian' AND
                        person_injury = 'Killed'
                    )
        """
        ```

        This uses a subquery in the `IN` clause to find all the values of `collision_id` in the `person` table where a pedestrian was killed. The effect will be to will limit the results to vehicles that have been in one of those collisions.

1. Set `sql` to the result of concatenating `sql_select`, `sql_from` and `sql_where`.

1. Set `veh` equal to the result of calling `pd.read_sql()` with arguments `sql` and `con`.

1. Write the data to a CSV file by calling `.to_csv()` on `veh` with arguments `"veh.csv"` and `index=False`.

1. Clean up the vehicle type data by setting `veh["type"]` equal to the result of calling `.str.replace()` on `veh["type"]` with arguments `"Sport Utility Vehicle"` and `"SUV"`. This shortens the long vehicle type name.

1. Clean up the pre-crash action data by setting `veh["pre_crash"]` equal to the result of calling `.str.replace()` on `veh["pre_crash"]` with arguments `"Other*"` and `"Other"`. This removes the asterisk from one of the categories.

1. Create a figure showing vehicle types by setting `fig` equal to the result of calling `topcats()` with three arguments: `veh["type"]`, `"Vehicle Types"`, and `limit=10`.

1. Save the figure by calling `.savefig()` on `fig` with argument `"fig8.png"`.

1. Create a figure showing driver license status by setting `fig` equal to the result of calling `topcats()` with three arguments: `veh["license"]`, `"License Status of Driver"`, and `limit=10`.

1. Save the figure by calling `.savefig()` on `fig` with argument `"fig9.png"`.

1. Create a figure showing pre-crash actions by setting `fig` equal to the result of calling `topcats()` with three arguments: `veh["pre_crash"]`, `"Pre-Crash Actions"`, and `limit=10`.

1. Save the figure by calling `.savefig()` on `fig` with argument `"fig10.png"`.

1. Create a histogram of driver ages by setting `fg` equal to the result of calling `sns.displot()` with three arguments: `veh`, `x="driver_age"`, `kind="hist"`, and `kde=True`.

1. Set the figure title by calling `.suptitle()` on `fg.figure` with argument `"Age of Driver"`.

1. Set the axis labels by calling `.set_axis_labels()` on `fg` with arguments `"Age"` and `"Number"`.

1. Finalize the layout by calling `.tight_layout()` on `fg`.

1. Save the figure by calling `.savefig()` on `fg` with argument `"fig11.png"`.

### I. Combining pedestrian and vehicle information

1. Merge the pedestrian and vehicle data by setting `merged` equal to the result of calling `.merge()` on `ped_trim` with three arguments: `veh`, `on="collision_id"`, and `validate="m:m"`. The `validate="m:m"` argument indicates this is a many-to-many merge (multiple pedestrians and vehicles can be involved in the same crash).

1. Set `grid` equal to the result of calling `.size()` on `merged` grouped by `["pre_crash","action"]`.

1. Reshape the data by setting `grid` equal to the result of calling `.unstack()` on `grid` with argument `"pre_crash"` and then calling `.fillna(0)` on the result.

1. Create a clustered heatmap by setting `cg` equal to the result of calling `sns.clustermap()` with three arguments: `grid`, `annot=True`, and `fmt=".0f"`. The `fmt=".0f"` argument formats the annotations as integers with no decimal places.

1. Set the X axis label by calling `.set_xlabel()` on `cg.ax_heatmap` with argument `"Vehicle Action"` and set the Y axis label by calling `.set_ylabel()` on `cg.ax_heatmap` with argument `"Pedestrian Action"`.

1. Save the figure by calling `.savefig()` on `cg` with argument `"fig12.png"`.

1. Close the database.

## Submitting

Once you're happy with everything and have committed all of the changes to your local repository, please push the changes to GitHub. At that point, you're done: you have submitted your answer. Note that the `.gitignore` file will exclude the `.db` and sample CSV files from your repository.

## Tips

* SQL is extremely powerful for extracting and aggregating data from large databases. The queries in this exercise demonstrate joins, subqueries, filtering with `WHERE` clauses, and grouping with `GROUP BY`.

* The `USING` keyword in SQL joins is a shorthand for joining on columns with the same name in both tables. It's equivalent to writing `ON left_table.column = right_table.column`.

* Seaborn's `clustermap()` function automatically reorders rows and columns to group similar patterns together. This makes it easier to spot relationships in the data.

* The `int|None` type hint syntax (using the vertical bar) indicates a parameter can be either an integer or None.

* The `.mask()` method is the opposite of `.where()`: it replaces values where the condition is True rather than where it's False.
