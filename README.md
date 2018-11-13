# camcommander

[![Build Status](https://travis-ci.org/tparker-usgs/camcommander.svg?branch=master)](https://travis-ci.org/tparker-usgs/camcommander)
[![Code Climate](https://codeclimate.com/github/tparker-usgs/camcommander/badges/gpa.svg)](https://codeclimate.com/github/tparker-usgs/camcommander)

## Configuration

  
## Installation

## Operation
Camcommander scripts are executed from a cron-like utility. They launch frequently, do their work, and exit. The task launcher makes sure that only one instance of each job runs at a time. This means that a job must run to compeltion before it will be launched again, which could cause a delay in retrieving images if images cannot be quickly shipped to all destinations. This is a consious trade-off made to gain resilicy and enable easy configuration updates.
  
