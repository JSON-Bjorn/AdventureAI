import React from 'react';
import { Box, Button, Container, Heading, Text, VStack } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  const handlePlayClick = () => {
    navigate('/game');
  };

  return (
    <Box bg="black" minH="100vh" display="flex" alignItems="center">
      <Container maxW="container.md">
        <VStack spacing={8} textAlign="center" color="white">
          <Heading size="2xl" mb={4}>
            Adventure AI
          </Heading>
          <Text fontSize="xl" mb={6}>
            Embark on an epic journey where your choices shape the story. 
            Experience a unique adventure powered by artificial intelligence.
          </Text>
          <Button
            colorScheme="purple"
            size="lg"
            onClick={handlePlayClick}
            _hover={{ transform: 'scale(1.05)' }}
            transition="all 0.2s"
          >
            Play Now
          </Button>
        </VStack>
      </Container>
    </Box>
  );
};

export default LandingPage; 