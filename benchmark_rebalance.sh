#!/bin/bash

# Funkcje pomocnicze
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

benchmark() {
    local input_file=$1
    local values=$(head -n 1 "$input_file")
    local num_nodes=$(echo "$values" | wc -w)
    local input_name=$(basename "$input_file" .txt)

    # Test dla AVL
    test_tree "$input_name" "$num_nodes" "$values" "AVL"
    
    # Test dla BST
    test_tree "$input_name" "$num_nodes" "$values" "BST"
}

test_tree() {
    local input_name=$1
    local num_nodes=$2
    local values=$3
    local tree_type=$4

    local input_data="values> $values\naction> rebalance\naction> exit\n"

    # Pomiar czasu konstrukcji drzewa
    local constr_start=$(date +%s.%N)
    echo -e "values> $values\naction> exit\n" | python3 drzewa.py --tree $tree_type >/dev/null 2>&1
    local constr_end=$(date +%s.%N)
    local constr_time=$(bc <<< "scale=9; ($constr_end - $constr_start) * 1000")

    # Pomiar czasu rebalansu
    local rebal_start=$(date +%s.%N)
    echo -e "$input_data" | python3 drzewa.py --tree $tree_type >/dev/null 2>&1
    local rebal_end=$(date +%s.%N)
    local rebal_time=$(bc <<< "scale=9; ($rebal_end - $rebal_start) * 1000")

    # Zapisz wyniki
    echo "$num_nodes,$input_name,$tree_type,$constr_time,$rebal_time" >> temp_results.csv
    
    printf "%-15s | %-6s | %-10s | %12s ms | %12s ms\n" \
           "$input_name" "$tree_type" "$num_nodes" "$constr_time" "$rebal_time"
}

# Inicjalizacja plików
echo "node_count,test_name,tree_type,construction_time,rebalance_time" > temp_results.csv

# Generuj dane jeśli brak
if [ ! -d "benchmark" ] || [ -z "$(ls benchmark)" ]; then
    echo "Generowanie danych testowych..."
    generate_test_data
fi

# Nagłówek wyników
echo "─────────────────────────────────────────────────────────────────────"
printf "%-15s | %-6s | %-10s | %14s | %14s\n" "Test" "Typ" "Rozmiar" "Czas konstrukcji" "Czas rebalansu"
echo "─────────────────────────────────────────────────────────────────────"

# Przeprowadzenie testów
for file in benchmark/*.txt; do
    benchmark "$file"
done

# Sortowanie wyników i zapis do finalnych plików
sort -t, -k1n temp_results.csv | awk -F, 'BEGIN {
    print "test_name,node_count,tree_type,construction_time,rebalance_time" > "benchmark_results.csv";
    print "test_name,node_count,construction_time,rebalance_time" > "avl_results.csv";
    print "test_name,node_count,construction_time,rebalance_time" > "bst_results.csv"
}
{
    if ($3 == "AVL") print $2","$1","$4","$5 >> "avl_results.csv";
    if ($3 == "BST") print $2","$1","$4","$5 >> "bst_results.csv";
    print $2","$1","$3","$4","$5 >> "benchmark_results.csv"
}'

# Usuń plik tymczasowy
rm temp_results.csv

echo "─────────────────────────────────────────────────────────────────────"
echo "Zapisano posortowane wyniki w:"
echo "- benchmark_results.csv (wszystkie wyniki)"
echo "- avl_results.csv (tylko AVL)"
echo "- bst_results.csv (tylko BST)"
