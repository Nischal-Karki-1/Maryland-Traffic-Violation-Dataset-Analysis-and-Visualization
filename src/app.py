from dash import Dash, html, dcc, page_container, callback, Input, Output, State
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True,
    suppress_callback_exceptions=True
)

def create_nav_buttons(active_path="/"):
    button_styles = {
        'base': {
            'borderRadius': '50%',
            'width': '35px',
            'height': '35px',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'fontSize': '18px',
            'fontWeight': 'bold'
        },
        'arrow': {
            'borderRadius': '50%',
            'width': '25px',
            'height': '25px',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'fontSize': '12px',
            'fontWeight': 'bold',
            'marginTop': '0.5%'
        }
    }

    pages = [
        {"number": "1", "path": "/"},
        {"number": "2", "path": "/demographics"},
        {"number": "3", "path": "/temporal"},
        {"number": "4", "path": "/vehicle"},
        {"number": "5", "path": "/price"},
        {"number": "6", "path": "/detailed"}
    ]

    current_page_index = next((i for i, page in enumerate(pages) if page["path"] == active_path), 0)
 
    prev_path = pages[max(0, current_page_index - 1)]["path"] if current_page_index > 0 else "/"
    next_path = pages[min(len(pages) - 1, current_page_index + 1)]["path"] if current_page_index < len(pages) - 1 else pages[-1]["path"]

    nav_buttons = [
        dbc.Button(
            "❮",
            href=prev_path,
            color="primary",
            className="me-3",
            style=button_styles['arrow']
        )
    ]

    for page in pages[:-1]: 
        is_active = active_path == page["path"]
        nav_buttons.append(
            dbc.Button(
                page["number"],
                href=page["path"],
                color="primary" if not is_active else "success",
                className="me-3",
                style={**button_styles['base'],
                       'backgroundColor': '#00008B' if is_active else None,
                       'borderColor': '#00008B' if is_active else None}
            )
        )

    nav_buttons.append(
        dbc.Button(
            "❯",
            href=next_path,
            color="primary",
            style=button_styles['arrow']
        )
    )

    return html.Div(nav_buttons, style={
        'display': 'flex',
        'justifyContent': 'center',
        'backgroundColor': 'white',
        'marginTop': '-15%'
    })

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(
        page_container,
        style={
            'padding': '20px',
            'paddingBottom': '100px',
            'minHeight': 'calc(100vh - 100px)'
        }
    ),
    html.Div(id='nav-buttons-container')
])

@callback(
    Output('nav-buttons-container', 'children'),
    Input('url', 'pathname')
)
def update_nav(pathname):
    return create_nav_buttons(pathname)

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)