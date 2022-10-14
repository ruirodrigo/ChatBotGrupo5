# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
class ActionBuscaPassagem(Action):

    def name(self) -> Text:
        return "buscar_passagens"

    #def buscar_passagens(origem, destino, data_ida, data_retorno, classe="ECO", itinerario="ROUND_TRIP"):
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

      origem = tracker.get_slot("origem")
      origem = str(origem)
      destino = tracker.get_slot("destino")
      destino = str(destino)
      classe = tracker.get_slot("classe")
      classe = str(classe)
      itinerario = tracker.get_slot("itinerario")
      itinerario = str(itinerario)
      data_ida = tracker.get_slot("data_ida")
      data_ida = str(data_ida)
      if str(itinerario).strip().upper()=="ROUND_TRIP":
        data_retorno = tracker.get_slot("data_retorno")
        data_retorno = str(data_retorno)
      else:
        data_retorno=""

      url = "https://priceline-com-provider.p.rapidapi.com/v1/flights/search"
      querystring = {
        "itinerary_type":itinerario,            #"ROUND_TRIP"/"ONE_WAY"
        "class_type":classe,                    #"ECO"/"BUS"/"PEC"/"PST"
        "sort_order":"PRICE",                   #"PRICE"/"ARRIVETIME"/"DEPARTTIME"/"TRAVELTIME"
        "location_departure":origem,
        "location_arrival":destino,
        "date_departure":data_ida,              #"2022-11-15", Formato da data
        "date_departure_return":data_retorno,   #"2022-11-16", #Somente em caso de ROUND_TRIP
        "number_of_stops":"0",
        "price_max":"20000",
        "number_of_passengers":"1",
        "duration_max":"2051",
        "price_min":"100"}

      headers = {
        "X-RapidAPI-Key": "2cd5c8051dmshd73dc2a440cd4b6p10a199jsnff3b16c84892",
        "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
      }
      response = requests.request("GET", url, headers=headers, params=querystring)
      jsonStr = response.text
      df = pd.read_json(StringIO(jsonStr), orient='records', nrows=1000, lines=True)

      if str(df['airline'].values).strip().upper() == "NAN":
        texto = "Não foram encontrado voos com esses critérios"
      else:
        df_ciasAereas = pd.DataFrame(df.airline[0])
        df_Horarios = pd.DataFrame(df.segment[0])
        dfvaloresPassagensTmp = pd.DataFrame(df.pricedItinerary[0])
        lista = []
        for textoCompleto in dfvaloresPassagensTmp['pricingInfo']:
          txtTratado = str(textoCompleto).split("'totalFare':")
          valor = str(txtTratado[1]).split(",")[0]
          lista.append(valor)
        dfvaloresPassagensTmp['values'] = lista

        df_ciasAereas.query("code == '" +  df_Horarios['marketingAirline'].values[0] + "'")
        companhia = df_ciasAereas['name'].values[0]

        valor = "USD" + dfvaloresPassagensTmp['values'][0]

        texto = f'''
        Um ótimo voo foi encontrado ->
        CIA Aérea: {companhia}
        Voo:  {df_Horarios['flightNumber'][0]} 
        Aeroporto de Origem: {df_Horarios['origAirport'][0]} 
        Aeroporto de Destino: {df_Horarios['destAirport'][0]} 
        Data/Hora da Partida: {df_Horarios['departDateTime'][0]}
        Data/Hora da chegada: {df_Horarios['arrivalDateTime'][0]}
        Valor: {valor} 
        '''
      dispatcher.utter_message(text=f"{texto}")
