from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import UploadedFile
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
import seaborn as sns
from django.shortcuts import render
import base64
from plotly.offline import plot
import plotly.express as px
import plotly.io as pio
import io

data = None  # Variable globale pour stocker les données

def upload_file(request):
    global data
    stats = None

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            data = pd.read_csv(file.file.path)
    else:
        form = UploadFileForm()

    if data is not None:
        stats = {
            'num_rows': len(data),
            'num_columns': len(data.columns),
            'columns': list(data.columns),
            'has_null_values': data.isnull().values.any(),  # Check for null values
            'null_count': data.isnull().sum().to_dict()  # Count nulls in each column

        }

    return render(request, 'upload_file.html', {
        'form': form,
        'stats': stats, 
    })

def data_preview(request):
    global data
    data_html = None
    filtered_data = data  # Create a copy to work with for filtering
    
    if data is not None:
        # Get filter parameters from GET request
        start_index = request.GET.get('start_index')
        end_index = request.GET.get('end_index')
        column_name = request.GET.get('column_name')
        
        try:
            # Apply row filtering if both indices are provided
            if start_index and end_index:
                start_idx = int(start_index)
                end_idx = int(end_index)
                
                # Ensure indices are within valid range
                start_idx = max(0, min(start_idx, len(filtered_data)))
                end_idx = max(0, min(end_idx, len(filtered_data)))
                
                # Apply row filter
                if start_idx < end_idx:
                    filtered_data = filtered_data.iloc[start_idx:end_idx]
            
            # Apply column filtering if column is specified
            if column_name:
                # Handle multiple column selection (assuming column_name could be a list)
                if isinstance(column_name, str):
                    columns = [col.strip() for col in column_name.split(',')]
                    # Filter only existing columns
                    valid_columns = [col for col in columns if col in filtered_data.columns]
                    if valid_columns:
                        filtered_data = filtered_data[valid_columns]
            
            # Convert the filtered data to HTML
            data_html = filtered_data.to_html(
                classes='data-table',
                index=False,
                border=1,
                justify='left'
            )
            
        except (ValueError, KeyError) as e:
            data_html = f"Error applying filters: {str(e)}"
    else:
        data_html = "No data available. Please upload a CSV file first."

    context = {
        'data_html': data_html,
        'columns': list(data.columns) if data is not None else [],
        'total_rows': len(data) if data is not None else 0,
        'current_filters': {
            'start_index': request.GET.get('start_index', ''),
            'end_index': request.GET.get('end_index', ''),
            'column_name': request.GET.get('column_name', '')
        }
    }
    
    return render(request, 'data_preview.html', context)

def access_row_column(request):
    global data
    row_data = None
    column_data = None
    error_message = None

    if request.method == 'GET':
        start_index = request.GET.get('start_index', None)
        end_index = request.GET.get('end_index', None)
        column_name = request.GET.get('column_name', None)

        # Valider les indices de lignes
        try:
            if start_index is not None and end_index is not None:
                start_index = int(start_index)
                end_index = int(end_index)

                # Accéder aux lignes selon la plage
                row_data = data.iloc[start_index:end_index].to_dict(orient="records")  # Convertir en liste de dictionnaires pour l'affichage
        except ValueError:
            error_message = "Les indices de ligne doivent être des entiers valides."

        # Accéder à la colonne spécifiée
        if column_name:
            if column_name in data.columns:
                column_data = data[column_name].to_list()  # Convertir la colonne en liste pour l'affichage
            else:
                error_message = "Le nom de colonne spécifié n'existe pas."

    return render(request, 'access_data.html', {
        'stats': {'error': error_message},
        'row_data': row_data,
        'column_data': column_data,
        'start_index': start_index,
        'end_index': end_index,
        'columns': data.columns if data is not None else [],
    })



def modify_data(request):
    global data

    if request.method == 'POST':
        column = request.POST.get('column')
        operation = request.POST.get('operation')
        value = float(request.POST.get('value', 0))

        if column in data.columns:
            if operation == 'add':
                data[column] += value
            elif operation == 'subtract':
                data[column] -= value
            elif operation == 'multiply':
                data[column] *= value
            elif operation == 'divide' and value != 0:
                data[column] /= value

    return redirect('upload_file')


def statistical_analysis(request):
    global data
    stats = None

    if data is not None:  # Check if data is loaded
        if request.method == 'GET':
            # Get the start and end indices from the GET request
            start_index = request.GET.get('start_index', None)
            end_index = request.GET.get('end_index', None)
            selected_column = request.GET.get('selected_column', None)

            if start_index and end_index and selected_column:
                try:
                    # Convert indices to integers
                    start_index = int(start_index)
                    end_index = int(end_index)

                    # Ensure the indices are within the valid range
                    if start_index < len(data) and end_index <= len(data) and start_index < end_index:
                        # Slice the DataFrame using iloc to get the rows within the specified range
                        subset = data.iloc[start_index:end_index]

                        # Select the desired column
                        if selected_column in subset.columns:
                            column_data = subset[selected_column]

                            # Calculate statistics for the selected column
                            stats = {
                                'mean': column_data.mean(),
                                'median': column_data.median(),
                                'std_dev': column_data.std(),
                                'min': column_data.min(),
                                'max': column_data.max(),
                                'count': column_data.count(),
                            }
                        else:
                            stats = {'error': f"Column '{selected_column}' not found in the selected range."}

                    else:
                        stats = {'error': 'Invalid range of indices. Ensure start < end and within valid row indices.'}
                except ValueError:
                    stats = {'error': 'Invalid indices provided. Ensure indices are numbers.'}

            else:
                stats = {'error': 'Please provide both start and end indices, and select a column.'}

    else:
        stats = {'error': 'No data available. Please upload a dataset.'}

    return render(request, 'statistics.html', {
        'stats': stats,
        'columns': data.columns if data is not None else [],
    })

def visualization(request):
    global data
    plot_div = None
    plot_type = request.GET.get('plot_type', 'scatter')
    column_x = request.GET.get('column_x')
    column_y = request.GET.get('column_y')

    if data is not None:
        try:
            if plot_type == 'scatter':
                fig = px.scatter(data, x=column_x, y=column_y, title="Scatter Plot")
            elif plot_type == 'line':
                fig = px.line(data, x=column_x, y=column_y, title="Line Plot")
            elif plot_type == 'bar':
                fig = px.bar(data, x=column_x, y=column_y, title="Bar Chart")
            elif plot_type == 'histogram':
                fig = px.histogram(data, x=column_x, title="Histogram")
            elif plot_type == 'box':
                fig = px.box(data, x=column_x, y=column_y, title="Box Plot")
            elif plot_type == 'pie' and column_x in data.columns:
                fig = px.pie(data, names=column_x, title="Pie Chart")
            elif plot_type == 'xy_line':
                fig = px.line(data, x=column_x, y=column_y, title="XY Line Graph")
            else:
                fig = None

            if fig:
                plot_div = plot(fig, output_type='div')
        except Exception as e:
            plot_div = f"An error occurred: {e}"

    return render(request, 'visualization.html', {
        'plot_div': plot_div,
        'columns': data.columns if data is not None else [],
    })