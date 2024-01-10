from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, expr, max

# Building Spark Session
spark = SparkSession.builder \
    .appName('Apache Spark Beginner Tutorial') \
    .config("spark.executor.memory", "1G") \
    .config("spark.executor.cores", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel('ERROR')

# Rutas de archivos
pathEquipo = r'C:\Users\ferra\Desktop\LEB-Scraper\Output\estadisticas_total_equipo.csv'
pathPartido = r'C:\Users\ferra\Desktop\LEB-Scraper\Output\partidos.csv'
pathJugadores = r'C:\Users\ferra\Desktop\LEB-Scraper\Output\player_stats.csv'

# Cargando DataFrames
dfEquipo = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(pathEquipo)
dfPartido = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(pathPartido)
dfJugadores = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(pathJugadores)

# Imprimiendo los esquemas de los DataFrames
print("Esquema de dfEquipo:")
dfEquipo.printSchema()
print("Esquema de dfPartido:")
dfPartido.printSchema()
print("Esquema de dfJugadores:")
dfJugadores.printSchema()

def calcular_media_faltas_por_arbitro(df, columna_arbitro):
    df_media_faltas = df.groupBy(columna_arbitro).agg(
        avg(col("faltas_local")).alias("faltas_local"),
        avg(col("faltas_visitante")).alias("faltas_visitante")
    )
    return df_media_faltas.withColumn(
        "faltas_totales", 
        expr("faltas_local + faltas_visitante")
    ).withColumnRenamed(columna_arbitro, "arbitro")

# Función para identificar a los líderes en cada categoría estadística
def identificar_lideres(df, categoria):
    return df.groupBy("nombre").agg(max(categoria).alias(f"max_{categoria}")).orderBy(col(f"max_{categoria}").desc())

def calcular_media_jugadores(df, categoria):
    return df.groupBy("nombre").agg(avg(categoria).alias(f"media_{categoria}")).orderBy(col(f"media_{categoria}").desc())


# Calculando el promedio de puntos por equipo
avg_points_per_team = dfEquipo.groupBy("equipo").agg(avg("puntos").alias("puntos_promedio"))
#avg_points_per_team.show()

# Uniendo dfEquipo con dfPartido para obtener faltas por equipo local y visitante
dfPartido_con_faltas = dfPartido.join(
    dfEquipo.select("id_partido", "equipo", "faltas_cometidas").alias("local"),
    (dfPartido.id_partido == col("local.id_partido")) & (dfPartido.nombre_local == col("local.equipo")), 
    "left"
).join(
    dfEquipo.select("id_partido", "equipo", "faltas_cometidas").alias("visitante"),
    (dfPartido.id_partido == col("visitante.id_partido")) & (dfPartido.nombre_visitante == col("visitante.equipo")), 
    "left"
).select(
    dfPartido["*"], col("local.faltas_cometidas").alias("faltas_local"), col("visitante.faltas_cometidas").alias("faltas_visitante")
)


# Calculando la media de faltas para cada árbitro
media_faltas_arbitro1 = calcular_media_faltas_por_arbitro(dfPartido_con_faltas, "arbitro1")
media_faltas_arbitro2 = calcular_media_faltas_por_arbitro(dfPartido_con_faltas, "arbitro2")
media_faltas_arbitro3 = calcular_media_faltas_por_arbitro(dfPartido_con_faltas, "arbitro3")

# Mostrando los resultados para cada árbitro
#media_faltas_arbitro1.orderBy("faltas_totales", ascending=True).show(truncate=False, n=1000)
#media_faltas_arbitro2.orderBy("faltas_totales", ascending=True).show(truncate=False, n=1000)
#media_faltas_arbitro3.orderBy("faltas_totales", ascending=True).show(truncate=False, n=1000)


# Identificando a los líderes en puntos, rebotes y asistencias
lideres_puntos = identificar_lideres(dfJugadores, "puntos")
lideres_rebotes = identificar_lideres(dfJugadores, "rebotes_totales")
lideres_asistencias = identificar_lideres(dfJugadores, "asistencias")

# Análisis del impacto de los jugadores en el resultado del partido
impacto_jugadores = dfJugadores.groupBy("nombre").agg(avg("+/-").alias("impacto_promedio")).orderBy(col("impacto_promedio").desc())

# Calculando el número de partidos jugados por cada jugador
partidos_por_jugador = dfJugadores.groupBy("nombre").count().withColumnRenamed("count", "PJ")

# Uniendo este DataFrame con dfJugadores para agregar la columna PJ
dfJugadores_con_pj = dfJugadores.join(partidos_por_jugador, "nombre")

# Calculando los tiros de campo y tiros libres fallados
dfJugadores_con_pj = dfJugadores_con_pj.withColumn("TC_fallados", col("T2 totales") + col("T3 totales") - col("T2 encestados") - col("T3 encestados"))
dfJugadores_con_pj = dfJugadores_con_pj.withColumn("TL_fallados", col("TL totales") - col("TL encestados"))

# Calculando la eficiencia de cada jugador
indice_eficiencia = dfJugadores_con_pj.withColumn(
    "eficiencia", 
    expr("(puntos + rebotes_totales + asistencias + recuperaciones + tapones_favor - TC_fallados - TL_fallados - perdidas) / PJ")
)

# Calculando la media de eficiencia para cada jugador
eficiencia_jugadores = indice_eficiencia.groupBy("nombre").agg(
    avg("eficiencia").alias("eficiencia_promedio")
).orderBy(col("eficiencia_promedio").desc())


# Mostrando los resultados
media_puntos = calcular_media_jugadores(dfJugadores, "puntos").show(truncate=False)
media_rebotes = calcular_media_jugadores(dfJugadores, "rebotes_totales").show(truncate=False)
media_asistencias = calcular_media_jugadores(dfJugadores, "asistencias").show(truncate=False)
impacto_jugadores.orderBy("impacto_promedio", ascending=False).show(truncate=False)
eficiencia_jugadores.orderBy("eficiencia_promedio", ascending=False).show(truncate=False)


# Deteniendo la sesión de Spark
spark.stop()