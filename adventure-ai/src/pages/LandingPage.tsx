import React from 'react';
import { Box, Button, Heading, VStack, Text } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

const LandingPage: React.FC = () => {
    const navigate = useNavigate();

    const handlePlayClick = () => {
        navigate('/game');
    };

    return (
        <Box
            bg="black"
            minH="100vh"
            display="flex"
            alignItems="center"
            justifyContent="center"
            p={4}
        >
            <VStack spacing={8}>
                <Heading color="white" size="2xl">
                    Adventure AI
                </Heading>
                <Text color="gray.300" fontSize="xl" textAlign="center" maxW="600px">
                    Embark on an AI-powered journey where your choices shape the story.
                    Experience a unique adventure every time with dynamic storytelling,
                    immersive visuals, and atmospheric audio.
                </Text>
                <Button
                    colorScheme="blue"
                    size="lg"
                    onClick={handlePlayClick}
                    px={12}
                    py={8}
                    fontSize="2xl"
                >
                    Play Now
                </Button>
            </VStack>
        </Box>
    );
};

export default LandingPage; 