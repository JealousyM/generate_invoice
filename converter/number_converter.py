"""
Number to words converter for Polish and English
"""

class NumberToWords:
    
    # Polish number names
    POLISH_UNITS = ['', 'jeden', 'dwa', 'trzy', 'cztery', 'pięć', 'sześć', 'siedem', 'osiem', 'dziewięć']
    POLISH_TEENS = ['dziesięć', 'jedenaście', 'dwanaście', 'trzynaście', 'czternaście', 
                   'piętnaście', 'szesnaście', 'siedemnaście', 'osiemnaście', 'dziewiętnaście']
    POLISH_TENS = ['', '', 'dwadzieścia', 'trzydzieści', 'czterdzieści', 'pięćdziesiąt',
                  'sześćdziesiąt', 'siedemdziesiąt', 'osiemdziesiąt', 'dziewięćdziesiąt']
    POLISH_HUNDREDS = ['', 'sto', 'dwieście', 'trzysta', 'czterysta', 'pięćset',
                      'sześćset', 'siedemset', 'osiemset', 'dziewięćset']
    
    # English number names
    ENGLISH_UNITS = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    ENGLISH_TEENS = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',
                    'sixteen', 'seventeen', 'eighteen', 'nineteen']
    ENGLISH_TENS = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
    
    @classmethod
    def to_polish(cls, amount):
        """Convert amount to Polish words"""
        try:
            amount_float = float(amount)
            euros = int(amount_float)
            cents = int((amount_float - euros) * 100)
            
            if euros == 0 and cents == 0:
                return "zero euro"
            
            result_parts = []
            
            if euros > 0:
                euro_words = cls._convert_number_polish(euros)
                if euros == 1:
                    result_parts.append(f"{euro_words} euro")
                elif euros in [2, 3, 4]:
                    result_parts.append(f"{euro_words} euro")
                else:
                    result_parts.append(f"{euro_words} euro")
            
            if cents > 0:
                cent_words = cls._convert_number_polish(cents)
                if cents == 1:
                    result_parts.append(f"{cent_words} cent")
                else:
                    result_parts.append(f"{cent_words} centów")
            
            return " ".join(result_parts)
            
        except (ValueError, TypeError):
            return "nieprawidłowa kwota"
    
    @classmethod
    def to_english(cls, amount):
        """Convert amount to English words"""
        try:
            amount_float = float(amount)
            euros = int(amount_float)
            cents = int((amount_float - euros) * 100)
            
            if euros == 0 and cents == 0:
                return "zero euro"
            
            result_parts = []
            
            if euros > 0:
                euro_words = cls._convert_number_english(euros)
                if euros == 1:
                    result_parts.append(f"{euro_words} euro")
                else:
                    result_parts.append(f"{euro_words} euro")
            
            if cents > 0:
                cent_words = cls._convert_number_english(cents)
                if cents == 1:
                    result_parts.append(f"{cent_words} cent")
                else:
                    result_parts.append(f"{cent_words} cents")
            
            return " ".join(result_parts)
            
        except (ValueError, TypeError):
            return "invalid amount"
    
    @classmethod
    def _convert_number_polish(cls, num):
        """Convert number to Polish words"""
        if num == 0:
            return ""
        
        if num < 1000:
            return cls._convert_hundreds_polish(num)
        
        if num < 1000000:
            thousands = num // 1000
            remainder = num % 1000
            
            result = cls._convert_hundreds_polish(thousands)
            if thousands == 1:
                result += " tysiąc"
            elif thousands in [2, 3, 4]:
                result += " tysiące"
            else:
                result += " tysięcy"
            
            if remainder > 0:
                result += " " + cls._convert_hundreds_polish(remainder)
            
            return result
        
        return str(num)  # Fallback for very large numbers
    
    @classmethod
    def _convert_number_english(cls, num):
        """Convert number to English words"""
        if num == 0:
            return ""
        
        if num < 1000:
            return cls._convert_hundreds_english(num)
        
        if num < 1000000:
            thousands = num // 1000
            remainder = num % 1000
            
            result = cls._convert_hundreds_english(thousands) + " thousand"
            
            if remainder > 0:
                result += " " + cls._convert_hundreds_english(remainder)
            
            return result
        
        return str(num)  # Fallback for very large numbers
    
    @classmethod
    def _convert_hundreds_polish(cls, num):
        """Convert number under 1000 to Polish words"""
        if num == 0:
            return ""
        
        result = []
        
        # Hundreds
        if num >= 100:
            result.append(cls.POLISH_HUNDREDS[num // 100])
            num %= 100
        
        # Tens and units
        if num >= 20:
            result.append(cls.POLISH_TENS[num // 10])
            if num % 10 > 0:
                result.append(cls.POLISH_UNITS[num % 10])
        elif num >= 10:
            result.append(cls.POLISH_TEENS[num - 10])
        elif num > 0:
            result.append(cls.POLISH_UNITS[num])
        
        return " ".join(result)
    
    @classmethod
    def _convert_hundreds_english(cls, num):
        """Convert number under 1000 to English words"""
        if num == 0:
            return ""
        
        result = []
        
        # Hundreds
        if num >= 100:
            result.append(cls.ENGLISH_UNITS[num // 100] + " hundred")
            num %= 100
        
        # Tens and units
        if num >= 20:
            result.append(cls.ENGLISH_TENS[num // 10])
            if num % 10 > 0:
                result.append(cls.ENGLISH_UNITS[num % 10])
        elif num >= 10:
            result.append(cls.ENGLISH_TEENS[num - 10])
        elif num > 0:
            result.append(cls.ENGLISH_UNITS[num])
        
        return " ".join(result)

