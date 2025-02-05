import React, { useState } from 'react';
import { Box, Grid, GridItem } from '@chakra-ui/react';
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
    const [isLoading, setIsLoading] = useState(false);
    const [imageUrl, setImageUrl] = useState<string>('');

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
                        <StoryDisplay />
                        <ActionInput onSubmit={onAction} disabled={isLoading} />
                        <Box>
                            <DiceRoll onRoll={onRoll} />
                        </Box>
                    </Grid>
                </GridItem>

                {/* Right Side - Image and Inventory */}
                <GridItem>
                    <Grid templateRows="2fr 1fr" h="100%" gap={4}>
                        <ImageDisplay imageUrl={imageUrl} isLoading={isLoading} />
                        <Box bg="gray.700" p={4} borderRadius="md">
                            <Box color="white" fontSize="xl" textAlign="center">
                                maybe like inventory or some shit
                            </Box>
                        </Box>
                    </Grid>
                </GridItem>
            </Grid>
            {isLoading && <LoadingOverlay isOpen={isLoading} message="Processing your action..." />}
        </Box>
    );
};

export default GameInterface; 