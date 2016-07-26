# coding: utf-8

# In[2]:

import sys, os

sys.path.append('..')
from backtester import matlab, backtester
from backtester.analysis import *
from backtester.strategy import StrategyBase, OptParam

import pandas as pd
import numpy as np
import scipy


class StrategyVolatilityCompression(StrategyBase):
    def __init__(self, strategy_context):
        # Initialize parent class
        super().__init__(strategy_context)

        # Define system's name
        self.name = 'VolatilityCompression'

        self.check_context()

        # Define optimized params
        self.opts = strategy_context['strategy']['opt_params']

    def check_context(self):
        #
        # Do strategy specific checks
        #
        pass

    #def calc_entry_rules(self, conversion_line_period, base_line_period, leading_spans_lookahead_period,
    #                     leading_span_b_period,
    #                     price_df):

        # return cloud_color_green, cloud_color_red, \
        #        price_above_cloud_top, price_above_cloud_bottom, \
        #        price_below_cloud_top, price_below_cloud_bottom, \
        #        price_crossup_base_line, price_crossdown_base_line, \
        #        price_crossup_conv_line, price_crossdown_base_line, \
        #        price_crossup_conv_line, price_crossdown_conv_line, \
        #        price_in_cloud, conv_crossup_base_line, \
        #        conv_crossdown_base_line, spans_crossup, \
        #        spans_crossdown


    def calculate(self, params=None, save_info=False):
        #
        #
        #  Params is a tripple like (50, 10, 15), where:
        #   50 - slow MA period
        #   10 - fast MA period
        #   15 - median period
        #
        #  On every iteration of swarming algorithm, parameter set will be different.
        #  For more information look inside: /notebooks/tmp/Swarming engine research.ipynb
        #

        if params is None:
            # Return default parameters
            direction, period_slow, period_fast, period_median = self.default_opts()
        else:
            # Unpacking optimization params
            #  in order in self.opts definition
            direction, period_slow, period_fast, period_median = params

        # Defining EXO price
        px = self.data.exo

        #
        #
        # Indicator calculation
        #
        #
        pctChg = px.pct_change()
        slow_volcomp = pctChg.rolling(period_slow).std() * np.sqrt(252)
        fast_volcomp = pctChg.rolling(period_fast).std() * np.sqrt(252)
        
        volComp = fast_volcomp / slow_volcomp
        
        # Median based trailing stop
        trailing_stop = px.rolling(period_median).median().shift(1)

        
        crossVal = fast_volcomp.copy()
        crossVal[:] = 0.5
        
        # Enry/exit rules
        if direction == 1 :   
            entry_rule = CrossUp(volComp, crossVal)
            
            exit_rule = (CrossDown(volComp, crossVal)) | (CrossDown(px, trailing_stop))
            
        elif direction == -1 :
            entry_rule = CrossDown(volComp, crossVal)
        
            exit_rule = (CrossUp(volComp, crossVal)) | (CrossDown(px, trailing_stop))
        
                

        # Swarm_member_name must be *unique* for every swarm member
        # We use params values for uniqueness
        swarm_member_name = self.get_member_name(params)

        #
        # Calculation info
        #
        calc_info = None
        if save_info:
            calc_info = {'trailing_stop': trailing_stop, 'slow_volcomp': slow_volcomp, 'fast_volcomp': fast_volcomp}

        return swarm_member_name, entry_rule, exit_rule, calc_info

if __name__ == "__main__":
    #
    #   Run this code only from direct shell execution
    #
    #strategy = StrategyVolatilityCompression()
    #equity, stats = strategy.calculate()

    # Do some work
    data, info = matlab.loaddata('../mat/strategy_270225.mat')
    data.plot()
