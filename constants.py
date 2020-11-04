from datetime import date

cities = ['Alcalá', 'Andalucía', 'Ansermanuevo', 'Argelia', 'Bolívar',
          'Buenaventura',	'Bugalagrande',	'Caicedonia', 'Cali', 'Calima - El Darién',
          'Candelaria', 'Cartago', 'Dagua', 'El Águila', 'El Cairo', 'El Cerrito',
          'El Dovio',	'Florida',	'Ginebra',	'Guacarí', 'Guadalajara de Buga', 'Jamundí',
          'La Cumbre', 'La Unión', 'La Victoria',	'Obando', 'Palmira', 'Pradera',
          'Restrepo', 'Riofrío', 'Roldanillo', 'San Pedro', 'Sevilla', 'Toro', 'Trujillo',
          'Tuluá', 'Ulloa', 'Versalles', 'Vijes',	'Yotoco', 'Yumbo', 'Zarzal']  # Ciudades Valle del Cauca
citiesLength = 42  # Número de ciudades
days = 20  # Proyección en días del modelo

epsilon = 12  # LOSS promedio
gompertzParamsLength = 6

citiesIndex = range(citiesLength)  # Indices de ciudades
daysIndex = range(days)  # Indices de días

sigmasPath = "./assets/sigmas.csv"
thetasPath = "./assets/thetas.csv"
gompertzPath = "./assets/gompertz.csv"
costsPath = "./assets/costs.csv"

startDate = date(2020, 3, 15)


def getElapsedDays():
    return abs((date.today() - startDate).days)
