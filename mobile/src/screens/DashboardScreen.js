import React, {useEffect, useState} from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { getSummary } from '../api';

export default function DashboardScreen(){
  const [summary, setSummary] = useState({});
  useEffect(()=>{
    (async ()=>{
      const s = await getSummary();
      setSummary(s);
    })();
  },[])

  return (
    <View style={styles.container}>
      <Text style={styles.title}>EcoSync Dashboard</Text>
      <View style={styles.card}><Text>Total Waste (kg): {summary.total_waste_kg}</Text></View>
      <View style={styles.card}><Text>Total Cooked (kg): {summary.total_cooked_kg}</Text></View>
      <View style={styles.card}><Text>Waste Ratio: {summary.waste_ratio}</Text></View>
    </View>
  )
}

const styles = StyleSheet.create({
  container:{flex:1,padding:20,backgroundColor:'#F3FBF6'},
  title:{fontSize:20,fontWeight:'700',color:'#004F4D',marginBottom:10},
  card:{padding:12,backgroundColor:'#fff',borderRadius:8,marginVertical:8}
});
