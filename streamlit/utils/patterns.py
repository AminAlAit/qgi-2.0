# Utility functions for pattern processing

def process_patterns(rows):
    # Process the raw pattern rows from the database into a structured format
    patterns = []
    for row in rows:
        pattern = {
            "org":            row[0],
            "version":        row[1],
            "main_name":      row[2],
            "index_name":     row[3],
            "country_a":      row[4],
            "country_b":      row[5],
            "pattern_length": row[6],
            "correlation":    row[7],
            "start_year_a":   row[8],
            "end_year_a":     row[9],
            "index_values_a": row[10],
            "start_year_b":   row[11],
            "end_year_b":     row[12],
            "index_values_b": row[13],
            "creation_date":  row[14],
            "matrix_profile": row[15],
            "unique_id":      row[16],
            "strength":       row[17]
        }
        patterns.append(pattern)
    return patterns
