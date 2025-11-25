import React, {useState} from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import { getAQIByCity } from '../api';

export default function AQIScreen(){
  const [city, setCity] = useState('Delhi');
  const [data, setData] = useState(null);

  async function handleFetch(){
    const res = await getAQIByCity(city);
    setData(res);
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Air Quality (AQI)</Text>
      <TextInput style={styles.input} value={city} onChangeText={setCity} />
      <Button title="Fetch AQI" onPress={handleFetch} />
      {data && <Text style={styles.result}>AQI: {JSON.stringify(data)}</Text>}
    </View>
  )
}

const styles = StyleSheet.create({
  container:{flex:1,padding:20,backgroundColor:'#F3FBF6'},
  title:{fontSize:20,fontWeight:'700',color:'#004F4D',marginBottom:10},
  input:{borderWidth:1,borderColor:'#cfeee0',padding:8,marginVertical:8,borderRadius:6,backgroundColor:'#fff'},
  result:{marginTop:20}
});
