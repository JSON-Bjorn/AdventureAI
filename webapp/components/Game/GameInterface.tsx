import React, { useState, useEffect } from 'react';
import { Box, VStack, useColorModeValue } from '@chakra-ui/react';
import StoryDisplay from './StoryDisplay';
import ActionInput from './ActionInput';
import ImageDisplay from './ImageDisplay';
import DiceRoll from './DiceRoll';
import LoadingOverlay from './LoadingOverlay';

interface GameInterfaceProps {
    onAction: (action: string) => void;
    onRoll: () => void;
}

const GameInterface: React.FC<GameInterfaceProps> = ({ onAction, onRoll }) => {
    const [story, setStory] = useState<string>('');
    const [currentImage, setCurrentImage] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [loadingMessage, setLoadingMessage] = useState<string>('');
    const [isDiceActive, setIsDiceActive] = useState<boolean>(false);
    const [diceRequirement, setDiceRequirement] = useState<number | null>(null);

    const bgColor = useColorModeValue('gray.900', 'gray.900');
    const textColor = useColorModeValue('white', 'white');

    return (
        <Box
            bg={bgColor}
            minH="100vh"
            p={4}
            color={textColor}
        >
            <VStack
                spacing={6}
                maxW="1600px"
                mx="auto"
                align="stretch"
            >
                <Box display="flex" gap={6} minH="768px">
                    <Box flex={1}>
                        <StoryDisplay
                            story={story}
                            isLoading={isLoading}
                        />
                        <ActionInput
                            onSubmit={onAction}
                            disabled={isLoading || isDiceActive}
                        />
                    </Box>
                    <Box w="768px">
                        <ImageDisplay
                            imageUrl={currentImage}
                            isLoading={isLoading}
                        />
                        {isDiceActive && (
                            <DiceRoll
                                requirement={diceRequirement}
                                onRoll={onRoll}
                            />
                        )}
                    </Box>
                </Box>
            </VStack>
            <LoadingOverlay
                isOpen={isLoading}
                message={loadingMessage}
            />
        </Box>
    );
};

export default GameInterface; 