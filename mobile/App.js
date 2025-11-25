import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from './src/screens/HomeScreen';
import MessScreen from './src/screens/MessScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import AQIScreen from './src/screens/AQIScreen';
import MenuOptScreen from './src/screens/MenuOptScreen';
import RedistributeScreen from './src/screens/RedistributeScreen';

const Stack = createStackNavigator();

export default function App(){
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home" screenOptions={{headerShown:false}}>
        <Stack.Screen name="Home" component={HomeScreen}/>
        <Stack.Screen name="Mess" component={MessScreen}/>
        <Stack.Screen name="MenuOpt" component={MenuOptScreen}/>
        <Stack.Screen name="Redistribute" component={RedistributeScreen}/>
        <Stack.Screen name="Dashboard" component={DashboardScreen}/>
        <Stack.Screen name="AQI" component={AQIScreen}/>
      </Stack.Navigator>
    </NavigationContainer>
  )
}
