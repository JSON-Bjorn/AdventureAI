import React, { useState, useEffect, useCallback } from 'react';
import { Box, Grid, GridItem, useToast } from '@chakra-ui/react';
import StoryDisplay from './StoryDisplay';
import ActionInput from './ActionInput';
import ImageDisplay from './ImageDisplay';
import DiceRoll from './DiceRoll';
import LoadingOverlay from './LoadingOverlay';
import { gameApi } from '../../services/gameApi';

interface GameState {
    story: string;
    image_url: string;
    needs_dice_roll: boolean;
    required_roll?: number;
    mood?: string;
    audio_url?: string;
}

const GameInterface: React.FC = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [gameState, setGameState] = useState<GameState | null>(null);
    const [previousStories, setPreviousStories] = useState<string[]>([]);
    const toast = useToast();

    // Initialize game on mount only
    useEffect(() => {
        const initializeGame = async () => {
            setIsLoading(true);
            try {
                const initialState = await gameApi.startGame();
                setGameState(initialState);
                setPreviousStories([initialState.story]);
            } catch (error) {
                toast({
                    title: 'Error',
                    description: 'Failed to start the game. Please try again.',
                    status: 'error',
                    duration: 5000,
                    isClosable: true,
                });
            }
            setIsLoading(false);
        };

        initializeGame();
    }, []); // Empty dependency array - only run once on mount

    const handleAction = async (action: string) => {
        if (!gameState) return;
        
        setIsLoading(true);
        try {
            const newState = await gameApi.submitAction(action, previousStories.slice(-4));
            setGameState(newState);
            
            if (!newState.needs_dice_roll) {
                setPreviousStories(prev => [...prev, newState.story]);
            }
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to process your action. Please try again.',
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        }
        setIsLoading(false);
    };

    const handleRoll = async () => {
        if (!gameState?.required_roll) return;
        
        setIsLoading(true);
        try {
            const newState = await gameApi.rollDice(gameState.required_roll);
            setGameState(newState);
            setPreviousStories(prev => [...prev, newState.story]);
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to process your roll. Please try again.',
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        }
        setIsLoading(false);
    };

    // Play audio when it changes
    useEffect(() => {
        if (gameState?.audio_url) {
            const audio = new Audio(gameState.audio_url);
            audio.play().catch(console.error);
        }
    }, [gameState?.audio_url]);

    return (
        <Box bg="black" minH="100vh" p={4}>
            <Grid
                templateColumns="1fr 1fr"
                gap={4}
                maxW="1800px"
                mx="auto"
                h="100vh"
            >
                {/* Left Side - Story and Controls */}
                <GridItem>
                    <Grid templateRows="1fr auto auto" h="100%" gap={4}>
                        <StoryDisplay story={gameState?.story || ''} />
                        <ActionInput 
                            onSubmit={handleAction} 
                            disabled={isLoading || (gameState?.needs_dice_roll ?? false)} 
                        />
                        <Box>
                            {gameState?.needs_dice_roll && (
                                <DiceRoll 
                                    onRoll={handleRoll}
                                    requiredRoll={gameState.required_roll}
                                    disabled={isLoading}
                                />
                            )}
                        </Box>
                    </Grid>
                </GridItem>

                {/* Right Side - Image and Inventory */}
                <GridItem>
                    <Grid templateRows="2fr 1fr" h="100%" gap={4}>
                        <ImageDisplay 
                            imageUrl={gameState?.image_url || ''} 
                            isLoading={isLoading} 
                        />
                        <Box bg="gray.700" p={4} borderRadius="md">
                            <Box color="white" fontSize="xl" textAlign="center">
                                {/* We can implement inventory later */}
                                Inventory Coming Soon
                            </Box>
                        </Box>
                    </Grid>
                </GridItem>
            </Grid>
            {isLoading && (
                <LoadingOverlay 
                    isOpen={isLoading} 
                    message={gameState?.needs_dice_roll ? "Rolling the dice..." : "Processing your action..."} 
                />
            )}
        </Box>
    );
};

export default GameInterface; 