interface GameState {
    story: string;
    image_url: string;
    needs_dice_roll: boolean;
    required_roll?: number;
    mood?: string;
    audio_url?: string;
}

const API_BASE_URL = 'http://localhost:8000';

export const gameApi = {
    startGame: async (): Promise<GameState> => {
        const response = await fetch(`${API_BASE_URL}/start-game`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        if (!response.ok) {
            throw new Error('Failed to start game');
        }
        
        return response.json();
    },

    submitAction: async (action: string, previousStories: string[] = []): Promise<GameState> => {
        const response = await fetch(`${API_BASE_URL}/player-action`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action,
                previous_stories: previousStories,
            }),
        });
        
        if (!response.ok) {
            throw new Error('Failed to process action');
        }
        
        return response.json();
    },

    rollDice: async (requiredRoll: number): Promise<GameState> => {
        const response = await fetch(`${API_BASE_URL}/roll-dice/${requiredRoll}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        if (!response.ok) {
            throw new Error('Failed to process dice roll');
        }
        
        return response.json();
    },
}; 