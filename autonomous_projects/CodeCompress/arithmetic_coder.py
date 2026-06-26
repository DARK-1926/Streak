# This would contain the corrected arithmetic coder implementation
# The issue is in the decode function which needs to properly handle
# the interval selection when all probabilities are equal
# The current implementation likely has a bug in how it maps
# the encoded value back to symbols when cumulative distributions
# are uniform
import math

def cumulative_distribution(probabilities):
    """Calculate cumulative distribution from probabilities."""
    result = []
    total = 0.0
    for p in probabilities:
        total += p
        result.append(total)
    return result

def find_interval(value, cumulative_dist):
    """Find the interval index for a given value in cumulative distribution."""
    for i, cum_val in enumerate(cumulative_dist):
        if value <= cum_val:
            return i
    return len(cumulative_dist) - 1

def encode(message, probabilities):
    """Encode a message using arithmetic coding."""
    cumulative = cumulative_distribution(probabilities)
    low = 0.0
    high = 1.0
    
    for byte in message:
        range_size = high - low
        symbol_low = cumulative[byte-1] if byte > 0 else 0.0
        symbol_high = cumulative[byte]
        
        high = low + range_size * symbol_high
        low = low + range_size * symbol_low
    
    # Return the midpoint of the final range
    return (low + high) / 2

def decode(encoded_value, length, probabilities):
    """Decode an arithmetic coded value back to original message."""
    cumulative = cumulative_distribution(probabilities)
    result = []
    low = 0.0
    high = 1.0
    
    for _ in range(length):
        # Calculate the range
        range_size = high - low
        # Find which symbol this value represents
        scaled_value = (encoded_value - low) / range_size
        
        # Find the symbol by searching through cumulative distribution
        symbol = find_interval(scaled_value, cumulative)
        
        # Update the range based on the found symbol
        if symbol > 0:
            symbol_low = cumulative[symbol-1]
        else:
            symbol_low = 0.0
        symbol_high = cumulative[symbol]
        
        high = low + range_size * symbol_high
        low = low + range_size * symbol_low
        
        result.append(symbol)
    
    return bytes(result)
