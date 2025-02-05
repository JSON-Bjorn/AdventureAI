import React from 'react';
import { ChakraProvider } from '@chakra-ui/react';
import GameInterface from '../components/Game/GameInterface';

const GameTest: React.FC = () => {
    const handleAction = (action: string) => {
        console.log('Player action:', action);
        // For testing, let's simulate a response
        setTimeout(() => {
            // Add test story content here
        }, 1500);
    };

    const handleRoll = () => {
        console.log('Dice rolled!');
        // Simulate dice roll
    };

    return (
        <ChakraProvider>
            <GameInterface
                onAction={handleAction}
                onRoll={handleRoll}
            />
        </ChakraProvider>
    );
};

export default GameTest; 