import psycopg2
import pandas as pd
import streamlit as st
import plotly.express as px

def obtener_contraseña(filepath, name):
    with open(filepath, 'r') as archivo:
        for linea in archivo:
            if linea.startswith(name + ":"):
                return linea.split(":", 1)[1].strip()
    return None

# Uso del método
filepath = "passwords.txt"; name = "postgres"
keys = [obtener_contraseña(filepath, name)]

conexion = psycopg2.connect(database="EnergyConsumption", user="postgres", password=keys[0])
cursor = conexion.cursor()

query = """ SELECT * FROM "LogSensor" """

#Ejecutamos la seleccion para hallar los datos 
cursor.execute(query)

# Obtener los resultados
resultados = cursor.fetchall()

# Convertir los resultados a un DataFrame de Pandas
values = ["Date","Time","Active Power","Reactive Power","Voltage","Intensity","Sub 1","Sub 2","Sub 3"]
df = pd.DataFrame(resultados, columns=values)
# Leer y aplicar el archivo CSS externo
with open('Styles/styles.css') as f:
    css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# ---------------------------------------
# *           STREAMLIT PAGE            *
# ---------------------------------------

st.title("Household Energy Consumption")
# Convertimos la columna "Date" a datetime si aún no lo está
df['Date'] = pd.to_datetime(df['Date'])

# Convertimos las columnas que deben ser numéricas
numeric_columns = ['Active Power', 'Reactive Power', 'Voltage', 'Intensity', 'Sub 1', 'Sub 2', 'Sub 3']

# Aseguramos que todas las columnas numéricas sean del tipo adecuado
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Calculamos el promedio diario
df_daily = df.groupby('Date')[numeric_columns].mean().reset_index()

#Creamos las variables de fechas maximas y minimas 
fecha_minima = df_daily['Date'].min()
fecha_maxima = df_daily['Date'].max()

#Cremos las columnas el desarrollo de los inputs
col1, col2 = st.columns(2)


#Damos los inputs para que el usuario decida las fechas
with col1:
    start_date = st.date_input('Fecha de inicio', fecha_minima, fecha_minima,fecha_maxima)

with col2:
    end_date = st.date_input('Fecha de fin', fecha_maxima, fecha_minima,fecha_maxima)

# Filtramos los datos por el rango de fechas seleccionado
df_filtered = df_daily[(df_daily['Date'] >= pd.to_datetime(start_date)) & (df_daily['Date'] <= pd.to_datetime(end_date))]

#Cremos las columnas el desarrollo de los inputs
col3, col4 = st.columns(2)

#Damos las columnas de los datos 
with col3:
    # Creamos un gráfico de líneas con plotly express para las métricas principales
    fig = px.line(df_filtered, x='Date', y=['Active Power', 'Reactive Power', 'Voltage', 'Intensity'],
                labels={'Date': 'Fecha', 'value': 'Promedio Diario', 'variable': 'Métricas'},
                title=f'Promedio Diario de las Métricas Eneregeticas')

    # Ajustamos la leyenda para que esté en la parte superior
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.001, xanchor="right", x=1))

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)
with col4:
    # Creamos otro gráfico de líneas para las métricas de Sub 1, Sub 2, y Sub 3
    fig_sub = px.line(df_filtered, x='Date', y=['Sub 1', 'Sub 2', 'Sub 3'],
                    labels={'Date': 'Fecha', 'value': 'Promedio Diario (W/h)', 'variable': 'Cuartos'},
                    title=f'Promedio Diario del Consumo Energético por Cuarto')
    
    # Ajustamos la leyenda para que esté en la parte superior
    fig_sub.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.001, xanchor="right", x=1))

    st.plotly_chart(fig_sub)
