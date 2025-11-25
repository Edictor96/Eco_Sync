import React, {useState} from 'react';
import { View, Text, TextInput, Button, StyleSheet, FlatList } from 'react-native';
import { optimizeMenu } from '../api';

export default function MenuOptScreen(){
  const [dishes, setDishes] = useState('[{"dish":"Rice","served":100,"waste":5},{"dish":"Paneer","served":80,"waste":12}]');
  const [result, setResult] = useState([]);

  async function handleOptimize(){
    try{
      const parsed = JSON.parse(dishes);
      const res = await optimizeMenu(parsed);
      setResult(res.optimized_menu);
    }catch(e){ alert('Invalid JSON') }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Menu Optimizer</Text>
      <TextInput style={styles.area} value={dishes} onChangeText={setDishes} multiline/>
      <Button title="Optimize Menu" onPress={handleOptimize}/>
      <FlatList data={result} renderItem={({item})=><Text style={styles.item}>{item}</Text>} keyExtractor={(i,idx)=>idx.toString()} />
    </View>
  )
}

const styles = StyleSheet.create({
  container:{flex:1,padding:20,backgroundColor:'#F3FBF6'},
  title:{fontSize:20,fontWeight:'700',color:'#004F4D',marginBottom:10},
  area:{borderWidth:1,borderColor:'#cfeee0',padding:8,marginVertical:8,borderRadius:6,backgroundColor:'#fff',height:120},
  item:{padding:10,fontSize:16}
});
