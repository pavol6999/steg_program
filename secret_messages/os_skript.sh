#! /bin/bash
#
# Meno: Pavol Krajkovic
# Kruzok: Piatok 8:00 Sys
# Datum: 7.12.2020
# Zadanie: zadanie07
#
# Text zadania:
#
# V zadanych adresaroch uvedenych ako argumenty najdite textove subory,
# v ktorych obsahu sa vyskytuje ich meno. Prehladavajte vsetky zadane adresare
# a aj ich podadresare.
# Ak nebude uvedena ako argument ziadna cesta, prehladava sa aktualny pracovny
# adresar (teda .).
# Ak bude skript spusteny s prepinacom -d <hlbka>, prehlada adresare len do
# hlbky <hlbka> (vratane). Hlbka znamena pocet adresarov na ceste medzi
# startovacim adresarom a spracovavanym suborom. Hlbka 1 znamena, ze bude
# prezerat subory len v priamo zadanych adresaroch.
#
# Syntax:
# zadanie.sh [-h][-d <hlbka>] [cesta ...]
#
# Vystup ma tvar:
# Output: '<cesta k najdenemu suboru> <pocet riadkov s menom suboru>'
#
# Priklad vystupu:
# Output: '/public/testovaci_adresar/testdir1/test 19'
#
# Program musi osetrovat pocet a spravnost argumentov. Program musi mat help,
# ktory sa vypise pri zadani argumentu -h a ma tvar:
# Meno programu (C) meno autora
#
# Usage: <meno_programu> <arg1> <arg2> ...
#    <arg1>: xxxxxx
#    <arg2>: yyyyy
#
# Parametre uvedene v <> treba nahradit skutocnymi hodnotami.
# Ked ma skript prehladavat adresare, tak vzdy treba prehladat vsetky zadane
# adresare a vsetky ich podadresare do hlbky.
# Pri hladani maxim alebo minim treba vzdy najst maximum (minimum) vo vsetkych
# zadanych adresaroch (suboroch) spolu. Ked viacero suborov (adresarov, ...)
# splna maximum (minimum), treba vypisat vsetky.
#
# Korektny vystup programu musi ist na standardny vystup (stdout).
# Chybovy vystup programu by mal ist na chybovy vystup (stderr).
# Chybovy vystup musi mat tvar (vratane apostrofov):
# Error: 'adresar, subor, ... pri ktorom nastala chyba': popis chyby ...
# Ak program pouziva nejake pomocne vypisy, musia mat tvar:
# Debug: vypis ...
#
# Poznamky: (sem vlozte pripadne poznamky k vypracovanemu zadaniu)
#
# Riesenie:


function help {
	echo "zadanie7 (C) Pavol Krajkovič"
	echo " "
	echo "Usage: z7.sh [-h] [-d <hlbka>] [cesta ...]"
	echo -e "	\033[1m -h, -H, --help \033[0m\n	 	Vypis help a ukonci program"
	echo -e "	\033[1m -d \033[4m<hlbka>\033[0m\033[0m\n		Prehlada adresare len do hlbky <hlbka> (vratane). Hlbka znamena pocet adresarov na ceste medzi startovacim adresarom a spracovavanym suborom.
"	
	 


}



depth=-1


#ziskaj z danych adresarov vsetky readable textove subory
get_files()
{	
	path="$@"
	
	
	if [ $depth == -1 ]; then
		#ak nebola zadana max hlbka	
		files="$(find "$path" -type f -readable -print  -exec grep -rIq . {} \; 2> >(sed -r 's/(grep:|find:)/Error:/'  >&2))"	
		
        else
                #ak bola zadana max hlbka
		files="$(find "$path" -maxdepth "$depth" -type f -readable -print  -exec grep -rIq . {} \; 2> >(sed -r 's/(grep:|find:)/Error:/'  >&2))"
		        fi
	echo "$files"
}


#zo vsetkych suborov sprav array, iteruj array a vypocitaj occurr_num, ktore predstavuje cislo vyskytu mena suboru v subore
file_matches()
{ 
	readarray -t arr <<< "$@"
	for file in "${arr[@]}"; do
		occurr_num=$(grep -ce "$(basename "$file")" "$file")
		if ((  $occurr_num >  0 )); then
			echo "Output: '$file $occurr_num'"	
		fi
	done

}


#array pre cesty k suborom
file_paths=()


#switch 
while (( "$#" )); do
	case "$1" in
		-h|-H|--help)		# vypis help
			help
			exit 0
			;;		
		-d|-D|-depth)		# nastavanie max hlbky
			shift 
			if [[ $1 =~ ^[0-9]+$ ]] ; then
				depth=$1
			else
				echo "Error: depth must be a positive integer number" 1>&2 && exit 1	
			fi
			shift
			;;
		-*)
			echo "Error: unknown predicate \`$1'" 1>&2		
			help
			exit 1
			;;

		*)	#ulozenie ciest suborov + check	
				
				
			file_paths+=("$1")
			shift
			;;
	esac
done


#ak nebola zadana ziadna cesta, prehladaj aktualny priecinok
if [ ${#file_paths[@]} -eq 0 ]; then	
	file_paths+='.'
fi



#ak bola ako hlbka zadana 0, tak automaticky exitni lebo ziadne subory find nenajde
if [ $depth -eq 0 ]; then
	exit 0
fi

#pre kazdu cestu spusti algoritmus
for path in "${file_paths[@]}"

do	
	if [ -d "$path" ]; then
		files=$(get_files "$path")
		file_matches "$files"	
	else
		echo "Error: $path, is not a directory" 	
	fi
done



