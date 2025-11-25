import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

export default function HomeScreen({navigation}){
  return (
    <View style={styles.container}>
      <Text style={styles.title}>EcoSync</Text>
      <TouchableOpacity style={styles.card} onPress={()=>navigation.navigate('Mess')}>
        <Text style={styles.cardText}>Smart Mess Planner</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.card} onPress={()=>navigation.navigate('MenuOpt')}>
        <Text style={styles.cardText}>Menu Optimizer</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.card} onPress={()=>navigation.navigate('Redistribute')}>
        <Text style={styles.cardText}>Redistribute Leftovers</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.card} onPress={()=>navigation.navigate('AQI')}>
        <Text style={styles.cardText}>Air Quality</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.card} onPress={()=>navigation.navigate('Dashboard')}>
        <Text style={styles.cardText}>Dashboard</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container:{flex:1,alignItems:'center',justifyContent:'center',backgroundColor:'#F3FBF6'},
  title:{fontSize:28,fontWeight:'700',color:'#004F4D',marginBottom:20},
  card:{width:'85%',padding:14,backgroundColor:'#fff',borderRadius:10,marginVertical:8,shadowColor:'#000',shadowOpacity:0.05,shadowRadius:6,elevation:3,alignItems:'center'},
  cardText:{fontSize:16,color:'#004F4D',fontWeight:'600'}
});
