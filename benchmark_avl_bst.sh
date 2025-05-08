#!/bin/bash

# Funkcja generująca dane testowe
generate_test_data() {
    mkdir -p benchmark
    max_pow=10

    for ((n=0; n<=max_pow; n++)); do
        size=$((2 ** n))
        values=$(seq 1 $size)
        
        echo "$values" | tr ' ' '\n' | shuf | tr '\n' ' ' > "benchmark/random_${size}.txt"
        echo "$values" > "benchmark/increasing_${size}.txt"
        echo "$values" | awk '{for(i=NF;i>0;i--) printf $i" "}' > "benchmark/decreasing_${size}.txt"
    done
}

# Funkcja benchmarkująca
benchmark() {
    local input_file=$1
    local tree_type=$2
    
    local values=$(head -n 1 "$input_file")
    local num_nodes=$(echo "$values" | wc -w)
    local input_name=$(basename "$input_file" .txt)

    local input_data="values> $values\naction> exit\n"

    local start_time=$(date +%s.%N)
    echo -e "$input_data" | python3 drzewa.py --tree $tree_type >/dev/null 2>&1
    local end_time=$(date +%s.%N)
    
    local exec_ms=$(bc <<< "scale=9; ($end_time - $start_time) * 1000")
    
    # Zapisz wyniki do pliku tymczasowego
    echo "$num_nodes,$input_name,$exec_ms,$tree_type" >> temp_results.csv
    
    printf "%-15s | %-6s | %-10s | %s ms\n" "$input_name" "$tree_type" "$num_nodes" "$exec_ms"
}

# Inicjalizacja plików
echo "node_count,test_name,time_ms,tree_type" > temp_results.csv

# Generuj dane jeśli brak
if [ ! -d "benchmark" ] || [ -z "$(ls benchmark)" ]; then
    echo "Generowanie danych testowych..."
    generate_test_data
fi

# Nagłówek wyników
echo "──────────────────────────────────────────────"
printf "%-15s | %-6s | %-10s | %s\n" "Test" "Typ" "Rozmiar" "Czas (ms)"
echo "──────────────────────────────────────────────"

# Przeprowadzenie testów
for file in benchmark/*.txt; do
    benchmark "$file" "AVL"
    benchmark "$file" "BST"
done

# Sortowanie wyników i zapis do finalnych plików
sort -t, -k1n temp_results.csv | awk -F, 'BEGIN {
    print "test_name,node_count,time_ms,tree_type" > "benchmark_results.csv";
    print "test_name,node_count,time_ms" > "avl_results.csv";
    print "test_name,node_count,time_ms" > "bst_results.csv"
}
{
    if ($4 == "AVL") print $2","$1","$3 >> "avl_results.csv";
    if ($4 == "BST") print $2","$1","$3 >> "bst_results.csv";
    print $2","$1","$3","$4 >> "benchmark_results.csv"
}'

# Usuń plik tymczasowy
rm temp_results.csv

echo "──────────────────────────────────────────────"
echo "Zapisano posortowane wyniki w:"
echo "- benchmark_results.csv (wszystkie wyniki)"
echo "- avl_results.csv (tylko AVL, posortowane)"
echo "- bst_results.csv (tylko BST, posortowane)"
