import React from 'react';
import GameInterface from '../components/Game/GameInterface';

const GameTest: React.FC = () => {
    const handleAction = (action: string) => {
        console.log('Player action:', action);
        setTimeout(() => {
            // Add test story content here
        }, 1500);
    };

    const handleRoll = () => {
        console.log('Dice rolled!');
    };

    return (
        <GameInterface
            onAction={handleAction}
            onRoll={handleRoll}
        />
    );
};

export default GameTest; 