# Transformations
A brief set of python functions for transforming en ef el data for optimization

## Purpose
When trying to run analysis for my fantasy team, I always  ended up with a bunch of odd csv/excel sheets. This is an example of a series of functions I use to clean, transform, and combine data sources.

## Requires
* Python 3.x
* [petl](https://github.com/petl-developers/petl)
* numpy
* pandas

## Setup
* Download salary csv from Draft Kings dot com. 
* Download play by play data from [nflsavant.com](www.nflsavant.com)

## Use
1. The files DKSalaries.csv and pbp-2018.csv should be in your working directory. 
2. Import ftbl_etl and call football_etl with a list of injured players. 
3. returns a Pandas dataframe that can be used for analysis

```
import ftbl_etl as fetl

injured_players = ['j.flacco', 'a.dalton']

fbl_df = fetl.football_etl(injured_players)
```
 
## Todo
1. Better handling for files (ie. names and location)
2. Speed optimization
3. clean up code

## Use
See license. 
