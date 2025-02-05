import React from 'react';
import GameInterface from './components/Game/GameInterface';

function App() {
    const handleAction = (action: string) => {
        console.log('Player action:', action);
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
}

export default App; 