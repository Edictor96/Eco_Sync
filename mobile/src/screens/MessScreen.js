import React, {useState} from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import { getPrediction } from '../api';

export default function MessScreen({navigation}){
  const [attendance, setAttendance] = useState('120');
  const [temp, setTemp] = useState('28');
  const [weekday, setWeekday] = useState('1');
  const [pred, setPred] = useState(null);

  async function handlePredict(){
    const payload = {attendance: Number(attendance), temp: Number(temp), weekday: Number(weekday), special_event: 0};
    const res = await getPrediction(payload);
    setPred(res.recommended_servings);
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Smart Mess Planner</Text>
      <TextInput style={styles.input} keyboardType="numeric" value={attendance} onChangeText={setAttendance} placeholder="Attendance"/>
      <TextInput style={styles.input} keyboardType="numeric" value={temp} onChangeText={setTemp} placeholder="Temperature"/>
      <TextInput style={styles.input} keyboardType="numeric" value={weekday} onChangeText={setWeekday} placeholder="Weekday (0-6)"/>
      <Button title="Predict Servings" onPress={handlePredict}/>
      {pred && <Text style={styles.pred}>Recommended Servings: {pred}</Text>}
    </View>
  )
}

const styles = StyleSheet.create({
  container:{flex:1,padding:20,backgroundColor:'#F3FBF6'},
  title:{fontSize:20,fontWeight:'700',color:'#004F4D',marginBottom:10},
  input:{borderWidth:1,borderColor:'#cfeee0',padding:8,marginVertical:8,borderRadius:6,backgroundColor:'#fff'},
  pred:{marginTop:20,fontSize:18,fontWeight:'700',color:'#00A86B'}
});
