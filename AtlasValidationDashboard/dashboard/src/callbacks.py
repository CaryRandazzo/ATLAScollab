##################
# Import modules #
##################
from dash.dependencies import Input, Output, State
import plotly.figure_factory as ff
import plotly.express as px
import scipy


###########################################
# Import python files and initialize data #
###########################################
from app import app


from chi2 import chi2df

# Initialize data and any errors
# df, errors = chi2df() # The current ploblem is here, its not called after subm
# print(df)

df, errors = None, None

@app.callback(
    Output('tmp', 'children'),
    Input('submit-button', 'n_clicks')
    )
def get_df(n_clicks):
    if n_clicks == 0:
        return

    print('WTFFF')
    global df, errors
    df, errors = chi2df()
    print('dfwtf',df)


##################
# UPDATE GRAPH 1 #
##################
@app.callback(
    Output('graph_1', 'figure'),
    Input('submit-button', 'n_clicks'),
    # [Input('submit-button', 'n_clicks')],
    # [State('dropdown', 'value'), 
    # State('range_slider', 'value'), 
    # State('check_list', 'value'),
    # State('radio_items', 'value')]
    )
# def update_graph_1(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
def update_graph_1(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        return

    print("upating graph 1")
    df_th1s = df[df['f_type']=='TH1']
    hist_data = [df_th1s['chi2ndf_vals'].values]    
    group_labels = ['distplot'] # name of the dataset
    fig = ff.create_distplot(hist_data, group_labels, show_hist=False, histnorm='')#,show_rug=False)
    fig.update_layout(title_text=f'TH1 Distplot',xaxis_title='Chi2/NDF')
    return fig



##################
# UPDATE GRAPH 2 #
##################
@app.callback(
    Output('graph_2', 'figure'),
    [Input('submit-button', 'n_clicks')],
    # [State('dropdown', 'value'), 
    # State('range_slider', 'value'), 
    # State('check_list', 'value'),
    # State('radio_items', 'value')]
    )
# def update_graph_2(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
def update_graph_2(n_clicks):    
    # if n_clicks == 0:
        # return

    df_th2s = df[df['f_type']=='TH2']
    hist_data = [df_th2s['chi2ndf_vals'].values]    
    group_labels = ['distplot'] # name of the dataset
    fig = ff.create_distplot(hist_data, group_labels, show_hist=False, histnorm='')
    fig.update_layout(title_text=f'TH2 Distplot',xaxis_title='Chi2/NDF')
    return fig


##################
# UPDATE GRAPH 3 #
##################
@app.callback(
    Output('graph_3', 'figure'),
    [Input('submit-button', 'n_clicks')],
    # [State('dropdown', 'value'), 
    # State('range_slider', 'value'), 
    # State('check_list', 'value'),
    # State('radio_items', 'value')]
    )
# def update_graph_3(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
def update_graph_3(n_clicks):
    # if n_clicks == 0:
        # return

    df_tp = df[df['f_type']=='TProfile']
    hist_data = [df_tp['chi2ndf_vals'].values]    
    group_labels = ['distplot'] # name of the dataset
    fig = ff.create_distplot(hist_data, group_labels, show_hist=False, histnorm='')
    fig.update_layout(title_text=f'TProfile Distplot',xaxis_title='Chi2/NDF')
    return fig


##################
# UPDATE GRAPH 4 #
##################
@app.callback(
    Output('graph_4', 'figure'),
    [Input('submit-button', 'n_clicks')],
    # [State('dropdown', 'value'),
    # State('range_slider', 'value'), 
    # State('check_list', 'value'),
    # State('radio_items', 'value')]
    )
# def update_graph_4(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
def update_graph_4(n_clicks):
    # if n_clicks == 0:
        # return

    df_th1s = df[df['f_type']=='TH1']
    print(df_th1s)
    fig = px.scatter(df_th1s, x="f_name", y="chi2ndf_vals", width=600,height=1050)
    fig.update_layout(title_text=f'TH1 Chi2/NDF values by hist',xaxis_title='hist', yaxis_title='Chi2/NDF values')
    return fig


################## 
# UPDATE GRAPH 5 #
##################
@app.callback(
    Output('graph_5', 'figure'),
    [Input('submit-button', 'n_clicks')],
    # [State('dropdown', 'value'), 
    # State('range_slider', 'value'), 
    # State('check_list', 'value'),
    # State('radio_items', 'value')]
    )
# def update_graph_5(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
def update_graph_5(n_clicks):    
    # if n_clicks == 0:
    #     return

    df_th2s = df[df['f_type']=='TH2']
    fig = px.scatter(df_th2s, x="f_name", y="chi2ndf_vals", width=600,height=1100)
    fig.update_layout(title_text=f'TH2 Chi2/NDF values by hist',xaxis_title='hist', yaxis_title='Chi2/NDF values')
    return fig


##################
# UPDATE GRAPH 6 #
##################
@app.callback(
    Output('graph_6', 'figure'),
    [Input('submit-button', 'n_clicks')],
    # [State('dropdown', 'value'), 
    # State('range_slider', 'value'), 
    # State('check_list', 'value'),
    # State('radio_items', 'value')]
    )
# def update_graph_6(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
def update_graph_6(n_clicks):
    # if n_clicks == 0:
    #     return

    df_tp = df[df['f_type']=='TProfile']
    fig = px.scatter(df_tp, x="f_name", y="chi2ndf_vals", width=600,height=920)
    fig.update_layout(title_text=f'TProfile Chi2/NDF values by hist',xaxis_title='hist', yaxis_title='Chi2/NDF values')
    return fig


#######################
# UPDATE CARD TITLE 1 #
#######################
@app.callback(
    Output('card_title_1', 'children'),
    [Input('submit-button', 'n_clicks')],
    # [State('dropdown', 'value'), 
    # State('range_slider', 'value'), 
    # State('check_list', 'value'),
    # State('radio_items', 'value')]
    )
# def update_card_title_1(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
def update_card_title_1(n_clicks):
    # if n_clicks == 0:
    #     return

    df_th1s = df[df['f_type']=='TH1']
    return f'{len(df_th1s.values)}'


######################
# UPDATE CARD TEXT 1 #
######################
@app.callback(
    Output('card_text_1', 'children'),
    [Input('submit-button', 'n_clicks')],
    # [State('dropdown', 'value'), 
    # State('range_slider', 'value'), 
    # State('check_list', 'value'),
    # State('radio_items', 'value')]
    )
# def update_card_text_1(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
def update_card_text_1(n_clicks):
    # if n_clicks == 0:
    #     return

    return f"No. TH1's"

#######################
# UPDATE CARD TITLE 2 #
#######################
@app.callback(
    Output('card_title_2', 'children'),
    [Input('submit-button', 'n_clicks')],
    # [State('dropdown', 'value'), 
    # State('range_slider', 'value'), 
    # State('check_list', 'value'),
    # State('radio_items', 'value')]
    )
# def update_card_title_2(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
def update_card_title_2(n_clicks):
    # if n_clicks == 0:
    #     return

    df_th2s = df[df['f_type']=='TH2']
    return f'{len(df_th2s.values)}'

######################
# UPDATE CARD TEXT 2 #
######################
@app.callback(
    Output('card_text_2', 'children'),
    [Input('submit-button', 'n_clicks')],
    # [State('dropdown', 'value'), 
    # State('range_slider', 'value'), 
    # State('check_list', 'value'),
    # State('radio_items', 'value')]
    )
# def update_card_text_2(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
def update_card_text_2(n_clicks):
    # if n_clicks == 0:
    #     return

    return f"No. TH2's"

#######################
# UPDATE CARD TITLE 3 #
#######################
@app.callback(
    Output('card_title_3', 'children'),
    [Input('submit-button', 'n_clicks')],
    # [State('dropdown', 'value'), 
    # State('range_slider', 'value'), 
    # State('check_list', 'value'),
    # State('radio_items', 'value')]
    )
# def update_card_title_3(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
def update_card_title_3(n_clicks):
    # if n_clicks == 0:
    #     return

    df_tp = df[df['f_type']=='TProfile']
    return f'{len(df_tp.values)}'

######################
# UPDATE CARD TEXT 3 #
######################
@app.callback(
    Output('card_text_3', 'children'),
    [Input('submit-button', 'n_clicks')],
    # [State('dropdown', 'value'), 
    # State('range_slider', 'value'), 
    # State('check_list', 'value'),
    # State('radio_items', 'value')]
    )
# def update_card_text_3(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
def update_card_text_3(n_clicks):
    # if n_clicks == 0:
    #     return

    return f"No. TProfile's"

#######################
# UPDATE CARD TITLE 4 #
#######################
@app.callback(
    Output('card_title_4', 'children'),
    [Input('submit-button', 'n_clicks')],
    # [State('dropdown', 'value'), 
    # State('range_slider', 'value'), 
    # State('check_list', 'value'),
    # State('radio_items', 'value')]
    )
# def update_card_title_4(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
def update_card_title_4(n_clicks):
    # if n_clicks == 0:
    #     return

    return f'{errors}'

######################
# UPDATE CARD TEXT 4 #
######################
@app.callback(
    Output('card_text_4', 'children'),
    [Input('submit-button', 'n_clicks')],
    # [State('dropdown', 'value'), 
    # State('range_slider', 'value'), 
    # State('check_list', 'value'),
    # State('radio_items', 'value')]
    )
# def update_card_text_4(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
def update_card_text_4(n_clicks):
    # if n_clicks == 0:
    #     return

    return f"Chi2Test Errors"

########################
# UPDATE transfer_vals #
########################
# @app.callback(
#     [Output('transfer_val1', 'children'),
#     Output('transfer_val2','children')],
#     [Input('submit-button', 'n_clicks')],
#     [State('text_input1','value'),
#      State('text_input2','value')]
#     )
# def update_transfer_vals(n_clicks,text_input1,text_input2):
    # return text_input1, text_input2


#############
# UPDATE df #
#############
# @app.callback(
#     Output('output-data-upload','children'),
#     [Input('submit-button', 'n_clicks')],
#     [State('upload-data-1','filename1')],
#     [State('upload-data-2','filename2')]
#     )
# def parse_dropdowns(n_clicks, filename1, filename2):

#     if n_clicks == 0:
#         return ''
#     if not filename1 or not filename2:
#         return 'Please upload two ROOT TFile files.'

#     with open ('/app/data/fileOne.txt','a+') as f:
#         # I need to make sure this writes only the file name and not the entire path
#         # If it writes the entire path, I need to split it and get [-1] for just the filename
#         f.write(filename1) 
#     with open ('/app/data/fileTwo.txt','a_') as f:
#         # ditto
#         f.write(filename2) 

        # content_type1, content_string1 = contents1.split(',')
        # content_type2, content_string2 = contents2.split(',')
        # print(content_type1, content_string1)
        # print(content_type2, content_string2)
        # file_contents1 = contents1.split(',')[1]
        # file_contents2 = contents2.split(',')[1]
        # decoded = base64.b64decode(content_string)
        # decoded1 = base64.b64decode(file_contents1)
        # decoded2 = base64.b64decode(file_contents2)
        # try:
        #     fileOne = ROOT.TFile.Open('/app/data/' + fileOne)
        # except Exception as e:
        #     print("Invalid fileOne.")
        #     print(e)

        # try:
        #     fileTwo = ROOT.TFile.Open('/app/data/' + fileTwo)
        # except Exception as e:
        #     print("Invalid fileTwo.")
        #     print(e)

        # with open('/app/data/' + filename1) as f1:
        #     f1.write(base64.b64decode(contents1))
        # with open('/app/data/' + filename2) as f2:
        #     f2.write(base64.b64decode(contents2))

        # fileTwo = ROOt.TFile.Open(decoded2)

    #defining these files should be done by input from a dash input box
    #print(type(text_input1))
    #print(type(text_input2))
    #try:      
        #file1 = ROOT.TFile.Open(text_input1)
        #file2 = ROOT.TFile.Open(text_input2) 
        #file1 = ROOT.TFile.Open('data15_13TeV.00276689.physics_Main.merge.HIST.f1051_h335._0001.1')
        #file2 = ROOT.TFile.Open('data15_13TeV.00276689.physics_Main.merge.HIST.f1052_h335._0001')
        
    #except:
    #    print('file error')
    #print(f'type:{type(file1)}') #THIS CURRENTLY IS THE MAIN PROBLEM
    #print(f'type:{type(file2)}') #THIS CURRENTLY IS THE MAIN PROBLEM
    #apparently, there is an issue with cppyy as the file type/class rather than ROOT/class
    #ask sawyer?
    #WORKAROUND: everything works fine if you can do the calculations outside of the callbacks
    #but i wont be able to input the file?
    #THEREALFIX - use cashe store @cache.memoize() to memorize the global store,
    # see https://dash.plotly.com/sharing-data-between-callbacks(Example 3)
    #maybe you can call the function() outside of the callback/def scope in a global scope
    #that way you can access the damn file1/file2 text input values from global
    #WORSTCASE - we use an external input.py file, import it (from input import *) and...
    #have it in the documentation that you need to manually input the filenames there to
    #
    
    #try:
        #get output on the main function based on the 2 input files
    #    f_path, chi2_dict,n_th1,n_th2,n_tp,errors = validate_uw_hists(file1,file2,'',{'f_name':[],'f_type':[],'chi2ndf_vals':[]},0,0,0,0)
    #except:
    #    print('procesing error')

    #try:
        #construct the dataframe
    #    df = pd.DataFrame(chi2_dict)
    #except:
    #    print('dataframe creation error')
    
    #my_string = str(Input('text_input1','value'))
    #print(my_string)
    #print(f"{str(Input('text_input1','value'))}")
    #print(f"-----------------num th1s:{df[df['f_type']=='TH1'].shape[0]}")
    #print('done')
    return #df #this may need to be returned as a json, see sharing data between callbacks

# @app.callback(
#     Output('output-data-upload2','children'),
#     [Input('upload-data2', 'contents')],
#     [State('upload-data2','filename')],
#     #  State('text_input2','value')]
#     )
# def parse_dropdown2(contents, filename):
#     """IN DEvELOPMENT ... not currently in use, can ignore all of this"""

#     if contents is not None:
#         # content_type, content_string = contents.split(',')
#         # print(content_type, content_string)
#         # decoded = base64.b64decode(content_string)
#         try:
#             fileTwo = ROOT.TFile.Open('/app/data/' + contents_string)
#         except Exception as e:
#             print("Invalid fileTwo.")
#             print(e)

#     return fileTwo