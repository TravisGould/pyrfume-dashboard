# Imports
from dash import Dash, dcc, html, Input, Output, State, dash_table, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pyrfume
import requests
import pandas as pd
from PIL import Image, ImageOps

# Create Dash instance
external_stylesheets = [dbc.themes.BOOTSTRAP]

app = Dash(
    __name__,
    title='Pyrfume Data Explorer', 
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True
)

server = app.server

# App run config settings
app_run_config = {
    'debug': True,
    'host': '127.0.0.1',
    'port': 8050
}

# Pyrfume color scheme
colors = {
    'pyrfume_blue': '#3670A1',
    'pyrfume_yellow': '#FFD636',
    'pyrfume_light_yellow': '#FFF0B5',
    'pyrfume_light_blue': '#85ACCC'
}

# Style config for tables
style_table = {
    'maxHeight': 500,
    'overflowY': 'scroll'
}
style_cell = {
    'overflow': 'hidden',
    'textOverflow': 'ellipsis'
}
style_header = {
    'color': colors['pyrfume_light_yellow'],
    'backgroundColor': colors['pyrfume_light_blue'],
    'fontWeight': 'bold'
}

# Get Pyrfume-Data inventory markdown
inventory = requests.get('https://raw.githubusercontent.com/pyrfume/pyrfume-data/main/tools/inventory.md').text    
inventory = inventory.replace('nbsp;', 'nbsp')

# Get pre-created list of archives & master molecule list
molecule_master_list = pd.read_csv('static/molecule_master_list.csv')
archives = pd.read_csv('static/archive_list.csv', header=None)[0].to_list()

# Uncomment below to have option to create master molecule list and archive list from scratch
# # Faster to read from file when in debug mode
# if app_run_config['debug']:
#     molecule_master_list = pd.read_csv('static/molecule_master_list.csv')
#     archives = pd.read_csv('static/archive_list.csv', header=None)[0].to_list()
# else:
#     archives = pyrfume.list_archives()
#     # Skip over archives that are not for sole datasources
#     archives = [arc for arc in archives if arc not in ['mordred', 'morgan', 'molecules', 'embedding', 'prediction_targets', 'tools']]

#     print('Generating master molecule list...')
#     all_molecules = {}
#     for arc in archives:
#         try:
#             all_molecules[arc] = pyrfume.load_data(f'{arc}/molecules.csv')
#         except:
#             print(f'No molecules.csv found for {arc}')
#     molecule_master_list = pd.concat(all_molecules, axis=0).reset_index().rename(columns={'level_0': 'Archive'})
#     molecule_master_list = molecule_master_list.set_index('CID').sort_index().drop_duplicates()
#     molecule_master_list = molecule_master_list[['MolecularWeight', 'IsomericSMILES', 'IUPACName', 'name', 'Archive']].reset_index()
#     print('Master molecule list complete')

# Header layout
header = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.Img(
                src='https://avatars3.githubusercontent.com/u/34174393?s=200&v=4',
                style={
                    'width': '90px',
                }
            ),
            width={'size': 'auto'}
        ),
        dbc.Col(
            html.B(
                'The Pyrfume Data Explorer',
                style={
                    'font-size': 40,
                    'textAlign': 'left',
                    'color': colors['pyrfume_blue']
                }
            )
        )
        ],
        align='center',
        class_name='g-0 ms-auto flex-nowrap text-nowrap mt-3 mt-md-0'
    )   
    ], 
    fluid=True,
    style={
        'padding': '5px 0px 5px 0px',
    }
)

# Footer layout
griz_logo = Image.open('static/GrizLogoandCoArtboard_1.png').convert('RGBA')

# Modify alpha channel to have transparent background
new_data = []
for pixel in griz_logo.getdata():
    if pixel[:3] == (255, 255, 255):
        new_data.append((255, 255, 255, 0))
    else:
        new_data.append(pixel)
griz_logo.putdata(new_data)

footer = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row([
                dbc.Col(
                    dbc.NavbarBrand(
                        'Dashboard by',
                        class_name='ms-2',
                        style={'color': colors['pyrfume_yellow']}
                    )
                ),
                dbc.Col(
                    html.Img(
                        src=griz_logo,
                        height='50px'
                    )
                )
                ],
            align='center', 
            class_name='g-0'
            ),
            href='https://grizanalytica.com/',
            target='_blank',
            style={'textDecoration': 'none'} 
        ),
        dbc.Row([
            dbc.Col(
                    dbc.NavItem(
                        dbc.NavLink(
                            'About Pyrfume',
                            style={'color': colors['pyrfume_yellow']},
                            href="https://pyrfume.org/",
                            external_link=True,
                            target='_blank')
                    )
                ),
            dbc.Col(
                dbc.NavItem(
                    dbc.NavLink(
                        'Pyrfume-Data Repo',
                        style={'color': colors['pyrfume_yellow']},
                        href='https://github.com/pyrfume/pyrfume-data',
                        external_link=True,
                        target='_blank')
                )
            )
            ],
            class_name='g-0 ms-auto flex-nowrap text-nowrap mt-3 mt-md-0',
            align='center'
        )
        ],
        fluid=True
    ),
    fixed='bottom',
    color=colors['pyrfume_blue'],
    dark=True
)

# Define tab layouts
tab_definitions = [
    ('Repository Inventory', 'tab-1'),
    ('Archive Explorer', 'tab-2'),
    ('Molecule Finder', 'tab-3'),
    ('Cross-Archive Search', 'tab-4')
]

tabs = dbc.Container([
    dbc.Tabs(
        [dbc.Tab(label=tup[0], tab_id=tup[1]) for tup in tab_definitions],
        id='tabs',
        active_tab='tab-1'
    ),
    dbc.Container(
        id="content",
        fluid=True,
        style={'padding': 0},
    )
    ],
    fluid=True,
    class_name='dbc'
)

# Function to create headers in tabs
def tab_header(heading='Tab Heading'):
    return dbc.Container(
        dbc.Alert(
            html.H4(
                heading,
                style={
                    'margin-top': 5,
                    'margin-bottom': 5,
                    'margin-left': 5
                }
            ),
            style={
                'padding': '10px 0px 10px 5px',
                'text-align': 'left',
                'color': colors['pyrfume_yellow'],
                'backgroundColor': colors['pyrfume_blue']
            }
        ),
        style={'padding': '10px 0px 10px 0px'},
        fluid=True
    )

# Repo inventory visualization
tab1 = dbc.Container([
    # Header
    tab_header('The Pyrfume-Data Repository Contents'),
    # Display inventory badges
    dbc.Container(
        dcc.Markdown(
            inventory,
            dangerously_allow_html=True
        ),
        style={
            'padding': '0px 0px 60px 0px',
            'text-align': 'left'
        },
        fluid=True
    )
    ],
    fluid=True,
    class_name='dbc'
)

# Archive explorer
tab2 = dbc.Container([
    # Header
    tab_header('Explore a Pyrfume Archive'),
    # Dropdown menus
    dbc.Row([
        dbc.Col([
            html.H6('Select an archive:'),
            dcc.Dropdown(
                id='archive-dd',
                options=[{'label': archive, 'value': archive} for archive in archives],
                value=archives[0],
                placeholder='Select an archive'
            )
            ], 
            width={'size': 4}
        ),
        dbc.Col([
            html.H6('Select file to display:'),
            dcc.Dropdown(
                id='file-dd',
                value='molecules.csv',
                placeholder='Select a file'
            )
            ],
            width={'size': 8}
        )
        ],
        style={'padding': '0px 0px 10px 0px'}
    ),
    # Archive contents
    dbc.Row([
        # Display for manifest
        dbc.Col(
            dbc.Alert(
                dcc.Markdown(
                    id='manifest-div',
                    dangerously_allow_html=True,
                    style={'color': 'black'}
                ),
                color=colors['pyrfume_light_blue'],
                style={'font-size': 12}
            ),
            width={'size': 4}
        ),
        # Display for file contents
        dbc.Col(
            id='file-display',
            width={'size': 8}
        )
    ])    
    ],
    fluid=True,
    style={'padding': '0px 0px 80px 0px'}
)

# Molecule search
tab3 = dbc.Container([
    # Header
    tab_header('Search for a Specific Molecule'),
    # Search criteria, results stats, & molecule structure image
    dbc.Row([
        # Search criteria
        dbc.Col([
            # Dropdown to select archive
            dbc.Row([
                dbc.Col(
                    html.H6('Search by:'),
                    width={'size': 'auto'}
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='molecule-search-by-dd',
                        options=[{'label': col, 'value': col} for col in molecule_master_list.columns if col != 'Archive'],
                        value='CID',
                        placeholder='Search by:',
                    ),
                    width={'size': 9}
                )
                ],
                style={
                    'padding': '0px 0px 10px 0px'
                }
            ),
            # Input to enter search value
            dbc.Row([
                dbc.Col(
                    html.H6(
                        'Search for:'
                    ),
                    width={'size': 'auto'}
                ),
                dbc.Col(
                    dcc.Input(
                        id='molecule-search-val',
                        type='text',
                        value='4',
                        placeholder='',
                        debounce=True,
                        style={'width':'100%'}
                    ),
                    width={'size': 9}
                )
                ]
            )
            ],
            width={'size': 4}
        ),
        # Display for results stats/info
        dbc.Col([
            html.Div(id='molecule-search-results-stats')
            ],
            width={'size': 4}
        ),
        # Display molecule structure
        dbc.Col([
            html.Div(id='molecule-structure')
            ],
            width={'size': 4},
            style={'textAlign': 'center'}
        )
    ]),
    # Display search results
    # Molecules found
    dbc.Row(
        html.Div(id='molecule-search-results'),
        style={'padding': '10px 0px 0px 0px'}   
    ),
    # Behavior/physics files
    dbc.Row(
        html.Div(id='behavior-results'),
        style={'padding': '10px 0px 10px 0px'}
    )
    ],
    fluid=True,
    class_name='dbc',
    style={'padding': '0px 0px 80px 0px'}
)

# Cross-archive search
tab4 = dbc.Container([
    # Header
    tab_header('Cross-Archive Search'),
    # Archive selection dropdown menu
    dbc.Row([
        html.H6('Select at Least Two Archives:'),
        dcc.Dropdown(
            id='multi-archive-dd',
            options=[{'label': archive, 'value': archive} for archive in archives],
            placeholder='Select archives',
            multi=True
        )
        ],
        style={'padding': '0px 0px 10px 0px'}
    ),
    # Search & Reset buttons
    dbc.Row([
        dbc.Col(
            dbc.ButtonGroup([
                dbc.Button(
                'Search',
                id='cross-arc-search-button',
                n_clicks=0,
                color='primary',
                className='me-1',
                outline=True
                ),
                dbc.Button(
                    'Reset',
                    id='cross-arc-reset-button',
                    n_clicks=0,
                    color='primary',
                    className='me-1',
                    outline=True
                )
                ]
            ),
            width={'size': 2}
        ),
        dbc.Col(
            id='common-mol-display',
            width={'size': 10}
        )   
        ],
        style={'padding': '0px 0px 10px 0px'}
    ),
    # Search results
    dbc.Row(
        html.Div(id='cross-search-results'),
        style={'padding': '0px 0px 10px 0px'}
    )
    ],
    fluid=True,
    class_name='dbc',
    style={'padding': '0px 0px 80px 0px'}
)

# Define app layout
app.layout = dbc.Container([
    header,
    tabs,
    footer
    ],
    fluid=True,
    class_name='dbc'
)


# ---- Callbacks ----

# Render tab content
@app.callback(
    Output('content', 'children'), 
    Input('tabs', 'active_tab')
)
def switch_tab(at):
    if at == 'tab-1':
        return tab1
    elif at == 'tab-2':
        return tab2
    elif at == 'tab-3':
        return tab3
    elif at == 'tab-4':
        return tab4


# Select archive
@app.callback(
    Output('manifest-div', 'children'),
    Output('file-dd', 'options'),
    Output('file-dd', 'value'),
    Input('archive-dd', 'value')
)
def select_archive(value):
    if value is None:
        raise PreventUpdate
    
    try:
        manifest = pyrfume.load_manifest(value)
    except:
        return f'**No manifest found for {value}:**<br><br>', [], None
    
    # Convert manifest contents to Markdown & get list of files in archive
    md = f'**Manifest for {value}:**<br><br>'
    tab_indent = '&nbsp;' * 4
    files = []

    for class_, d in manifest.items():
        md += f'{class_}:<br>'
        for k, v in d.items():
            if k == 'tags':
                v = ', '.join(v.split(';'))
            md += f'{tab_indent} - **{k}**: {v}<br>'
        md += '<br>'

        if class_ not in ['source']:
            files += [k for k in d.keys() if '*' not in k]

    opt = [{'label': f, 'value': f} for f in files]

    if 'molecules.csv' in manifest['processed']:
        initial_file = 'molecules.csv'
    elif 'stimuli.csv' in manifest['processed']:
        initial_file = 'stimuli.csv'
    else:
        initial_file = None

    return md, opt, initial_file


# Create tables with tooltips that show molecule structure on hover
def table_with_tooltips(df):
    table = [
        dbc.Table(
            # Header
            [html.Thead([html.Tr([html.Th(col) for col in df.columns])], style={'color': colors['pyrfume_light_yellow'], 'backgroundColor': colors['pyrfume_light_blue']})] +
            # Body
            [html.Tbody([html.Tr([html.Td(df.iloc[i][col]) for col in df.columns], id=f'row_{i}') for i in range(df.shape[0])])],
            striped=True,
            hover=True
        )
    ]
    for i in range(df.shape[0]):
        smiles = df.iloc[i]['IsomericSMILES']
        im = pyrfume.odorants.smiles_to_image(smiles, png=False)
        bbox = ImageOps.invert(im).getbbox()
        im = html.Img(src=im.crop(bbox), style={'width': '75%', 'height': '75%'}) 
        table += [dbc.Tooltip(im, target=f'row_{i}', placement='top', style={'max-width': '100%'})]

    return table


# Display an archive file's contents
@app.callback(
    Output('file-display', 'children'),
    Input('file-dd', 'value'),
    State('archive-dd', 'value')
)
def display_file(f, arc):
    if f is None:
        raise PreventUpdate
    
    ext = f.split('.')[-1]
    
    if ext in ['csv', 'xls', 'xlsx']:
        df = pyrfume.load_data(f'{arc}/{f}').reset_index()
        if f.split('.')[0] == 'molecules':
            content = table_with_tooltips(df)
        else:
            content = dash_table.DataTable(
                df.to_dict('records'),
                id='table',
                style_header=style_header,
                style_table=style_table,
                style_cell=style_cell
            )
    elif ext in ['py', 'md', 'txt']:
        text = requests.get(f'https://raw.githubusercontent.com/pyrfume/pyrfume-data/main/{arc}/{f}').text
        if ext in ['py', 'md']:
            if ext == 'py':
                text = f'''```python \
                    {text}
                ```'''
            content = dcc.Markdown(
                text,
                dedent=True
            )
        else:
            content = html.Div(
                text,
                style={
                    'whiteSpace': 'pre-line',
                    'font-size': '14px'
                }
            )
    elif ext == 'LICENSE':
        manifest = pyrfume.load_manifest(arc)
        text = manifest['raw']['LICENSE']
        content = dbc.Alert(
            text,
            color='info',
            style={
                'whiteSpace': 'pre-line',
                'font-size': '14px'
            }
        )
    elif ext == 'pdf':
        content = html.Iframe(
            src=f'https://raw.githubusercontent.com/pyrfume/pyrfume-data/main/{arc}/{f}'
        )
    else:
        content = dbc.Alert(
            f'File type .{ext} not currently supported for display',
            color='warning'
        )
    return content


# Search all archives for a specific molecule
@app.callback(
    Output('molecule-search-results', 'children'),
    Output('molecule-search-results-stats', 'children'),
    Output('molecule-structure', 'children'),
    Input('molecule-search-val', 'value'),
    State('molecule-search-by-dd', 'value')
)
def molecule_search(val, col):
    if val is None:
        raise PreventUpdate

    structure = None
    
    # Format search value appropriately
    if col in ['CID', 'IsomericSMILES', 'IUPACName', 'name']:
        if col == 'CID':
            val = int(val)
        elif col == 'IsomericSMILES':
            val = val.upper()
        elif col in ['IUPACName', 'name']:
            val = val.lower()
        df = molecule_master_list[molecule_master_list[col] == val]
    elif col == 'MolecularWeight':
        val = float(val)
        df = molecule_master_list[molecule_master_list[col].between(val - 0.1, val + 0.1)]
    
    # Create output depending on # of results found
    if df.shape[0] > 0:
        df = df.sort_index().sort_values('Archive')
        results_text = [f'Returned {df.shape[0]} result(s) for {col}={val}']
        results_info_color = colors['pyrfume_light_blue']
        columns = [{'id': x, 'name': x} for x in df.columns if x != 'CID']

        if len(df.CID.unique()) > 1:
            df.loc[:, 'CID'] = df.CID.apply(lambda x: f'[{x}](https://pubchem.ncbi.nlm.nih.gov/compound/{x})')
            columns.insert(0, {'id': 'CID', 'name': 'CID', 'presentation': 'markdown'})
            results_text += [
                html.Br(),
                'Click on a CID to view the molecule on PubChem'
            ]
        else:
            columns.insert(0, {'id': 'CID', 'name': 'CID'})
            
            # Add link to PubChem if valid CID
            if df.iloc[0].CID > 0:
                results_text += [
                    html.Br(),
                    'View molecule on ',
                    html.A(
                        'PubChem',
                        href=f'https://pubchem.ncbi.nlm.nih.gov/compound/{df.iloc[0].CID}',
                        target='_blank',
                        className='alert-link'
                    )
                ]

            # Try to generate structure for molecule
            smiles = df.iloc[0].IsomericSMILES
            try:
                im = pyrfume.odorants.smiles_to_image(smiles, png=False)
                bbox = ImageOps.invert(im).getbbox()
                im = im.crop(bbox)

                structure = html.Img(
                    src=im,
                    style={
                        'display':'inline',
                        'width': '30%',
                        'height': '30%'
                    }
                )
            except:
                structure = dbc.Alert(
                    f'Could not compute structure for {smiles}',
                    color=colors['pyrfume_light_yellow']
                )
    else:
        results_text = [f'No molecules with {col}={val} can be found in the Pyrfume-Data repository']
        results_info_color = colors['pyrfume_light_yellow']
        columns = None
    
    results_info = dbc.Alert(
        results_text,
        color=results_info_color,
        style={'width': '100%'}
    )
    tbl = dash_table.DataTable(
            df.to_dict('records'),
            id='mol-search-table',
            columns=columns,
            style_header=style_header,
            style_table=style_table,
            style_cell=style_cell
        )

    table_div = [tbl, html.Div('Click on a row to load behavior/physics data')] if df.shape[0] > 0 else tbl

    return table_div, results_info, structure


# Load behavior/physics data on table click
@app.callback(
    Output('behavior-results', 'children'),
    Input('mol-search-table', 'active_cell'),
    Input('mol-search-table', 'data'),
    prevent_initial_call=True
)
def load_behavior(active_cell, data):
    if active_cell is None:
        return None
   
    cid = data[active_cell['row']]['CID']
    arc = data[active_cell['row']]['Archive']

    # If cid is a string, need to get actual cid out of the markdown text
    if isinstance(cid, str):
        cid = int(cid.split(']')[0][1:])

    # Get [processed] section from manifest to determine available files
    processed = pyrfume.load_manifest(arc)['processed']
    files = [key for key in processed.keys() if ('behavior' in key) or ('physics' in key)]

    # Get behavior & physcis files that are available
    if len(files) > 0:
        # Check for stimuli.csv
        if 'stimuli.csv' in processed.keys():
            stimuli = pyrfume.load_data(f'{arc}/stimuli.csv')
            drop_list = ['CAS', 'cas', 'MolecularWeight', 'IsomericSMILES', 'IUPACName', 'name']
            drop_cols = [col for col in drop_list if col in stimuli.columns]
            stimuli.drop(columns=drop_cols, inplace=True)
        else:
            stimuli = None
        
        content = []
        for f in files:
            column_order = []

            try:
                df = pyrfume.load_data(f'{arc}/{f}')

                if (stimuli is not None) and (df.index.name == 'Stimulus'):
                    df = df.join(stimuli)
            
                # Filter for the selected CID
                if 'CID' in df.columns:
                    df = df[(df.index == cid) | (df.CID == cid)].reset_index()
                else:
                    df = df[df.index == cid].reset_index()
                
                if df.shape[0] > 0:
                    # Rearragne columns so that first two columns are Stimulus and CID
                    column_order += [col for col in df.columns if 'CID' in col]
                    column_order += [col for col in df.columns if (col != 'Stimulus') and ('CID' not in col)]
                    if 'Stimulus' in df.columns:
                        column_order.insert(0, 'Stimulus')
                    df = df[column_order]

                    tbl = dash_table.DataTable(
                            df.to_dict('records'),
                            style_header=style_header,
                            style_table=style_table,
                            style_cell=style_cell
                    )
                else:
                    tbl = dbc.Alert(f'CID={cid} not in {f}', color=colors['pyrfume_light_yellow'])
                
                content += [
                    html.Hr(),
                    html.B(f'{f}:'),
                    html.P(f'{processed[f]}'),
                    tbl
                ]
            except:
                content += [
                    html.Hr(),
                    dbc.Alert(f'Could not process {f} from {arc}', color=colors['pyrfume_light_yellow'])
                ]
    else:
        content = [
            html.Hr(),
            dbc.Alert(f'No behavior or physics files in {arc}', color=colors['pyrfume_light_yellow'])
        ]
    return content


# Find molecules in common across selected archives
@app.callback(
    Output('cross-search-results', 'children'),
    Output('common-mol-display', 'children'),
    Output('multi-archive-dd', 'value'),
    Input('cross-arc-search-button', 'n_clicks'),
    Input('cross-arc-reset-button', 'n_clicks'),
    State('multi-archive-dd', 'value'),
    prevent_initial_call=True
)
def triage_cross_archive_search(n1, n2, archive_list):
    triggered_id = ctx.triggered_id
    if triggered_id == 'cross-arc-search-button':
        return cross_archive_search(archive_list)
    elif triggered_id == 'cross-arc-reset-button':
        return reset_tab_display()

def reset_tab_display():
    return None, None, ''

def cross_archive_search(archive_list):
    if (archive_list is None) or (len(archive_list) < 2):
        raise PreventUpdate

    df = molecule_master_list[molecule_master_list['Archive'].isin(archive_list)].sort_index().reset_index()
    df = df.groupby(['CID', 'MolecularWeight', 'IsomericSMILES', 'IUPACName', 'name']).size().reset_index(name='counts')
    df = df[df.counts == len(archive_list)]
    df.drop('counts', axis=1, inplace=True)

    stats = dbc.Alert(
        f'{df.shape[0]} molecules in common between {*archive_list,}',
        id='multi-archive-search-stats',
        color=colors['pyrfume_light_blue'],
        style={'width': '100%'}
    )

    tbl = table_with_tooltips(df)

    # tbl = dash_table.DataTable(
    #         df.to_dict('records'),
    #         id='multi-archive-search-table',
    #         style_header=style_header,
    #         style_table=style_table,
    #         style_cell=style_cell
    #     )
    return tbl, stats, archive_list


# Run config 
if __name__ == '__main__':
    app.run(**app_run_config)