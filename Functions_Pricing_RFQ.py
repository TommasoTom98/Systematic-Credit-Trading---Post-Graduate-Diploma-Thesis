import pandas as pd
import numpy as np
import datetime as dt
from IPython.display import display, HTML

import warnings
warnings.filterwarnings("ignore")

###############################################

def RFQ_Ticker_Price(df, Axes_threshold, Size_threshold, Target_Position, Print_DF = True):
    """
    Function that prices RFQs for single European Corporate Bonds.
                              *** Input *** 
    ° DataFrame with Columns: 
       - Side 
       - Notional 
       - Bid / Ask Price 
       - CBBT Bid / Ask 
       - Axes Bid 
    ° Axes_threshold = Threshold for Axed condition
    ° Size_threshold = Threshold for Size condition
    """
    Start = dt.datetime.now()
    
    pd.options.display.float_format = "{:,.3f}".format  # Round everything to the 3rd decimal place


    DataFrame = df.copy()

    DataFrame["w spread"] = (DataFrame["CBBT Ask"] - DataFrame["CBBT Bid"])
    DataFrame["CBBT Mid"] = (DataFrame["CBBT Bid"] + DataFrame["CBBT Ask"]) / 2

    if np.isnan(DataFrame["CBBT Mid"]).any():
        print("WARNING! Some CBBT*mid do not have a valid value!")

    ############################
    # Side
    
    Ask_Side = DataFrame["Side"].eq("Sell")
    Bid_Side = DataFrame["Side"].eq("Buy") 
    
    ############################
    # Axes Condition
    
    DataFrame["Axes"] = np.where(Ask_Side, np.where(DataFrame["AXES Ask"] > Axes_threshold, "Axed", "Not Axed"),
                                           np.where(DataFrame["AXES Bid"] > Axes_threshold, "Axed", "Not Axed")) 

    Cond_Axed_Buy = (Ask_Side) & (DataFrame["Axes"].eq("Axed"))
    Cond_Not_Axed_Buy = (Ask_Side) & (DataFrame["Axes"].eq("Not Axed"))

    Cond_Axed_Sell = (Bid_Side) & (DataFrame["Axes"].eq("Axed")) 
    Cond_Not_Axed_Sell = (Bid_Side) & (DataFrame["Axes"].eq("Not Axed"))
    
    ############################
    # Size Condition
    
    Distanza_iniziale = (DataFrame["Current position"] - Target_Position).abs()
    
    DataFrame["Final position"] = np.where(Ask_Side, DataFrame["Current position"] - DataFrame["Notional"],
                                          DataFrame["Current position"] + DataFrame["Notional"])
    
    DataFrame["Residual"] = np.abs(DataFrame["Final position"] - Target_Position).astype(int)
    
    DataFrame["Size"] = np.where((DataFrame["Residual"] <= Size_threshold) | (DataFrame["Residual"] < Distanza_iniziale),
                                 "Acceptable", "Not acceptable")
    
    Cond_Size_Acc_Buy = (Ask_Side) & (DataFrame["Size"] == "Acceptable")
    Cond_Size_Not_Acc_Buy = (Ask_Side) & (DataFrame["Size"] == "Not acceptable")
    
    Cond_Size_Acc_Sell = (Bid_Side) & (DataFrame["Size"] == "Acceptable")
    Cond_Size_Not_Acc_Sell = (Bid_Side) & (DataFrame["Size"] == "Not acceptable")
    
    ############################
    # Axes type
    
    condizione = (DataFrame["AXES Bid"]  + DataFrame["AXES Ask"]) != 0
    Axes_type = np.where(condizione, DataFrame["AXES Ask"] / (DataFrame["AXES Bid"] + DataFrame["AXES Ask"]), 0.5)
    
    Cond_w_spread_1 = (Axes_type < 0.25)
    Cond_w_spread_2 = (Axes_type >= 0.25) & (Axes_type <= 0.75)
    Cond_w_spread_3 = (Axes_type > 0.75)
    DataFrame["Axes type"] = np.select([Cond_w_spread_1, Cond_w_spread_2, Cond_w_spread_3],
                                       ["Axe Bid only", "Axed", "Axe Ask only"],
                                       default="Not Axed")
    
    #############################
    ######### CBBT* mid #########
    #############################
    
    # CBBT Bid/ask
    
    Cond_onlyBid = (DataFrame["AXES Bid"] >= Axes_threshold) & (DataFrame["AXES Ask"] == 0)
    Cond_onlyAsk = (DataFrame["AXES Bid"] == 0) & (DataFrame["AXES Ask"] >= Axes_threshold)
    Cond_NoAxes = (DataFrame["AXES Bid"] == 0) & (DataFrame["AXES Ask"] == 0)
    
    ##############
    #   PRICES   # 
    ##############

    ### Axed ###

    # Not Acceptable Size
    Price_1 = np.where(Ask_Side, DataFrame["CBBT Mid"] + 0.5 * DataFrame["w spread"],   # Buy
                                  DataFrame["CBBT Mid"])                                 # Sell
                                         
    Price_2 = np.where(Ask_Side, DataFrame["CBBT Ask"] - 0.25 * DataFrame["w spread"],  # Buy
                                  DataFrame["CBBT Bid"] + 0.25 * DataFrame["w spread"])  # Sell
    
    Price_3 = np.where(Ask_Side, DataFrame["CBBT Ask"],                                 # Buy
                                  DataFrame["CBBT Bid"] - 0.5 * DataFrame["w spread"])   # Sell
    
    # Acceptable Size
    Price_4 = np.where(Ask_Side, DataFrame["CBBT Mid"] + 0.25 * DataFrame["w spread"],   # Buy
                                  DataFrame["CBBT Mid"] + 0.125 * DataFrame["w spread"])  # Sell
    
    Price_5 = np.where(Ask_Side, DataFrame["CBBT Ask"] - 0.25 * DataFrame["w spread"],   # Buy
                                  DataFrame["CBBT Bid"] + 0.25 * DataFrame["w spread"])   # Sell
    
    Price_6 = np.where(Ask_Side, DataFrame["CBBT Mid"] - 0.125 * DataFrame["w spread"],   # Buy
                                  DataFrame["CBBT Mid"] - 0.25 * DataFrame["w spread"])    # Sell
    
    
    ### Not Axed ###
    
    # Not Acceptable Size
    Price_7 = np.where(Ask_Side, DataFrame["CBBT Mid"] + 0.5 * DataFrame["w spread"],   # Buy
                                  DataFrame["CBBT Mid"] - 0.5 * DataFrame["w spread"])   # Sell
                            
    Price_8 = np.where(Ask_Side, DataFrame["CBBT Mid"] + 0.25 * DataFrame["w spread"],   # Buy
                                  DataFrame["CBBT Mid"] - 0.25 * DataFrame["w spread"])   # Sell
                            
    Price_9 = np.where(Ask_Side, DataFrame["CBBT Ask"] + 0.5 * DataFrame["w spread"],   # Buy
                                  DataFrame["CBBT Mid"] - 0.5 * DataFrame["w spread"])   # Sell
    
    # Acceptable Size
    Price_10 = np.where(Ask_Side, DataFrame["CBBT Mid"] + 0.375 * DataFrame["w spread"],  # Buy
                                   DataFrame["CBBT Mid"] - 0.125 * DataFrame["w spread"])  # Sell
                 
    Price_11 = np.where(Ask_Side, DataFrame["CBBT Mid"] + 0.25 * DataFrame["w spread"],   # Buy
                                   DataFrame["CBBT Mid"] - 0.25 * DataFrame["w spread"])   # Sell
                 
    Price_12 = np.where(Ask_Side, DataFrame["CBBT Mid"] + 0.125 * DataFrame["w spread"],   # Buy
                                   DataFrame["CBBT Mid"] - 0.375 * DataFrame["w spread"])   # Sell
    
    
    ##################
    #   CONDITIONS   # 
    ##################
    
    ### Axed ###
    
    # Not Acceptable Size
    Cond_Price_1 = (Cond_Axed_Buy & Cond_Size_Not_Acc_Buy & Cond_w_spread_1) | (Cond_Axed_Sell & Cond_Size_Not_Acc_Sell & Cond_w_spread_1)

    Cond_Price_2 = (Cond_Axed_Buy & Cond_Size_Not_Acc_Buy & Cond_w_spread_2) | (Cond_Axed_Sell & Cond_Size_Not_Acc_Sell & Cond_w_spread_2)
                             
    Cond_Price_3 = (Cond_Axed_Buy & Cond_Size_Not_Acc_Buy & Cond_w_spread_3) | (Cond_Axed_Sell & Cond_Size_Not_Acc_Sell & Cond_w_spread_3)
                            
    # Acceptable Size
    Cond_Price_4 = (Cond_Axed_Buy & Cond_Size_Acc_Buy & Cond_w_spread_1) | (Cond_Axed_Sell & Cond_Size_Acc_Sell & Cond_w_spread_1)
    
    Cond_Price_5 = (Cond_Axed_Buy & Cond_Size_Acc_Buy & Cond_w_spread_2) | (Cond_Axed_Sell & Cond_Size_Acc_Sell & Cond_w_spread_2)
    
    Cond_Price_6 = (Cond_Axed_Buy & Cond_Size_Acc_Buy & Cond_w_spread_3) | (Cond_Axed_Sell & Cond_Size_Acc_Sell & Cond_w_spread_3)
    
    
    ### Not Axed ###
        
    # Not Acceptable Size
    Cond_Price_7 = ((Cond_Not_Axed_Buy | Cond_NoAxes) & Cond_Size_Not_Acc_Buy & Cond_w_spread_1) | ((Cond_Not_Axed_Sell | Cond_NoAxes) & Cond_Size_Not_Acc_Sell & Cond_w_spread_1)
    
    Cond_Price_8 = ((Cond_Not_Axed_Buy | Cond_NoAxes) & Cond_Size_Not_Acc_Buy & Cond_w_spread_2) | ((Cond_Not_Axed_Sell | Cond_NoAxes) & Cond_Size_Not_Acc_Sell & Cond_w_spread_2)
    
    Cond_Price_9 = ((Cond_Not_Axed_Buy | Cond_NoAxes) & Cond_Size_Not_Acc_Buy & Cond_w_spread_3) | ((Cond_Not_Axed_Sell | Cond_NoAxes) & Cond_Size_Not_Acc_Sell & Cond_w_spread_3)
    
    # Acceptable Size
    Cond_Price_10 = ((Cond_Not_Axed_Buy | Cond_NoAxes) & Cond_Size_Acc_Buy & Cond_w_spread_1) | ((Cond_Not_Axed_Sell | Cond_NoAxes) & Cond_Size_Acc_Sell & Cond_w_spread_1)
    
    Cond_Price_11 = ((Cond_Not_Axed_Buy | Cond_NoAxes) & Cond_Size_Acc_Buy & Cond_w_spread_2) | ((Cond_Not_Axed_Sell | Cond_NoAxes) & Cond_Size_Acc_Sell & Cond_w_spread_2)
    
    Cond_Price_12 = ((Cond_Not_Axed_Buy | Cond_NoAxes) & Cond_Size_Acc_Buy & Cond_w_spread_3) | ((Cond_Not_Axed_Sell | Cond_NoAxes) & Cond_Size_Acc_Sell & Cond_w_spread_3)
    
    ###################
    
    DataFrame["RFQ Price"] = np.select([Cond_Price_1, Cond_Price_2, Cond_Price_3, Cond_Price_4, 
                                        Cond_Price_5, Cond_Price_6, Cond_Price_7, Cond_Price_8, 
                                        Cond_Price_9, Cond_Price_10, Cond_Price_11, Cond_Price_12],
                                    
                                       [Price_1, Price_2, Price_3, Price_4, 
                                        Price_5, Price_6, Price_7, Price_8,
                                        Price_9, Price_10, Price_11, Price_12],
                                       default = np.nan)

    if DataFrame["RFQ Price"].isna().any():
        print("WARNING! Some RFQ Prices do not have a valid value!")
    
    ###########################
    ###### Final Price #######
    ###########################
    
    DataFrame["RFQ Price"] = DataFrame["RFQ Price"].astype("float")
    col = ["CBBT Bid","CBBT Ask","CBBT Mid","w spread"]
    DataFrame[col] = DataFrame[col].apply(pd.to_numeric, errors="coerce")
    
    ############################
    End = dt.datetime.now()
    TimeDelta = End - Start
    ms = TimeDelta.total_seconds() * 1000
    
    #pd.options.display.float_format = "{:,.2f}".format
    DataFrame.columns.name = None
    DataFrame.index = range(1, len(DataFrame) + 1)
    
    if Print_DF == True:
        print("Source: BBGBTS_CREDIT", "", "Counterparty: BPF SGR", "", "Status RFQ: Done")
        display(HTML("<style>.dataframe td, .dataframe th {font-size: 11px;}</style>"))
        display(DataFrame)

    ################################
    ###### Performance Report ######
    ################################
    print("------------------------------------------------------------")
    print("         * * *      Single RFQ Prices        * * *          ")
    print("------------------------------------------------------------")
    print("")
    display(DataFrame[["ISIN", "RFQ Price"]])
    print("")
    print("------------------------------------------------------------")
    print("        * * *         Time Statistics         * * *         ")
    print("------------------------------------------------------------")
    print("")
    print("Start Time:                                ", Start.strftime("%H:%M:%S%f"))
    print("End Time:                                  ", End.strftime("%H:%M:%S%f"))
    print("                                             --------------")
    print(f"Execution time:                                   {ms:.2f} ms")
    
    return DataFrame
