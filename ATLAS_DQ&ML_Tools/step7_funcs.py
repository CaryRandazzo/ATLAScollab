def input_heatmap(df,ftag_id,hist_id):
    tmp = df[df['ftag_id']==ftag_id]
    tmp = tmp[tmp['hist_id']==hist_id]
    sns.heatmap( tmp.pivot_table(index='y',columns='x',values='occ') )