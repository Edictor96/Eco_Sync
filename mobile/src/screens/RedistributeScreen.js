import React, {useState} from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import { postWasteLog } from '../api';

export default function RedistributeScreen(){
  const [dish, setDish] = useState('Rice');
  const [cooked, setCooked] = useState('10');
  const [consumed, setConsumed] = useState('8');
  const [wasted, setWasted] = useState('2');

  async function handleLog(){
    const payload = {date: new Date().toISOString().split('T')[0], dish, cooked: Number(cooked), consumed: Number(consumed), wasted: Number(wasted)};
    const res = await postWasteLog(payload);
    if(res.status==='ok') alert('Logged');
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Redistribute / Log Leftovers</Text>
      <TextInput style={styles.input} value={dish} onChangeText={setDish} />
      <TextInput style={styles.input} keyboardType='numeric' value={cooked} onChangeText={setCooked} />
      <TextInput style={styles.input} keyboardType='numeric' value={consumed} onChangeText={setConsumed} />
      <TextInput style={styles.input} keyboardType='numeric' value={wasted} onChangeText={setWasted} />
      <Button title="Log / Post" onPress={handleLog} />
    </View>
  )
}

const styles = StyleSheet.create({
  container:{flex:1,padding:20,backgroundColor:'#F3FBF6'},
  title:{fontSize:20,fontWeight:'700',color:'#004F4D',marginBottom:10},
  input:{borderWidth:1,borderColor:'#cfeee0',padding:8,marginVertical:8,borderRadius:6,backgroundColor:'#fff'}
});
