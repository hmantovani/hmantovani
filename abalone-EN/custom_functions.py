def highlight_columns(df, rows=20, bg_color='lightgreen', text_color='black', columns_to_color=[], columns_to_show=[]):
    bg_style = f'background-color: {bg_color}; color: {text_color}'
    
    if len(columns_to_show) != 0:
        df = df[columns_to_show]
    
    def apply_style(data):
        return [bg_style if col in columns_to_color else '' for col in data.index]

    highlighted_df = df.style.apply(apply_style, axis=1)
    return highlighted_df