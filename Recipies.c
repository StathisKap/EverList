/* <DESC>
 * Very simple HTTP GET
 * </DESC>
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <curl/curl.h>

struct MemoryStruct {
  char *memory;
  size_t size;
};

static size_t WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp);
char * find_Ingredients(char * response); 

//******MAIN******//
int main(int argc, char **argv)
{
  CURL *curl;
  CURLcode res;
  FILE * out = fopen("Recipe.txt","w");
  struct MemoryStruct chunk;
  chunk.memory = malloc(1);  /* will be grown as needed by the realloc at the WriteMemoryCallback function*/
  chunk.size = 0;    /* no data at this point */

  curl = curl_easy_init();
  if(curl) {
    curl_easy_setopt(curl, CURLOPT_URL, argv[argc -1]); // Sets the url to the last given argument
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L); // Follows Redirects
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION,WriteMemoryCallback); // Sets the callback function to a function which always increases the memory allocated to our buffer
    curl_easy_setopt(curl, CURLOPT_WRITEDATA,(void*) &chunk); // sets the buffer to which everything is returned to, equal to &chunk instead of stdout
    curl_easy_setopt(curl, CURLOPT_USERAGENT, "libcurl-agent/1.0"); // Gives our request a user agent (some servers prefer it)

    /* Perform the request, res will get the return code */
    res = curl_easy_perform(curl);

    /* Check for errors */
    if(res != CURLE_OK){
      fprintf(stderr, "curl_easy_perform() failed: %s\n",
      curl_easy_strerror(res));
      return 1;
    }
    
    printf("%lu bytes retrieved\n", (unsigned long)chunk.size);
    char * ingredients_list = find_Ingredients(chunk.memory);
    // fprintf(out,"<a href=\"%s\" rev=\"en_rl_none\" class=\"en-link\"><u>%s</u></a>",argv[argc -1],/*Title of the dish*/);
    fprintf(out,"%s",ingredients_list);

    /* always cleanup */
    curl_easy_cleanup(curl);
    curl_global_cleanup();
    fclose(out);
    free(chunk.memory);
    free(ingredients_list);
  }
  return 0;
}



static size_t
WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp)
{
  size_t realsize = size * nmemb;
  struct MemoryStruct *mem = (struct MemoryStruct *)userp;
 
  char *ptr = realloc(mem->memory, mem->size + realsize + 1);
  if(!ptr) {
    /* out of memory! */
    printf("not enough memory (realloc returned NULL)\n");
    return 0;
  }
 
  mem->memory = ptr;
  memcpy(&(mem->memory[mem->size]), contents, realsize);
  mem->size += realsize;
  mem->memory[mem->size] = 0;
 
  return realsize;
}


char * find_Ingredients(char * response)
{ 
  char string_to_search_for[] =  "recipeIngredient";
  int size = strlen(string_to_search_for);
  char * recipe_Ingredient = strstr(response,string_to_search_for);
  char * recipe_Ingredient_end = recipe_Ingredient;
  char *ingredients_list = malloc(1);
  int ingredients_list_size = 0;

  if (recipe_Ingredient != NULL){
    printf("Found it!\n");
    recipe_Ingredient += size + 3;
    while (1)
    {
      recipe_Ingredient_end++;
      if(*recipe_Ingredient_end == ']')
        break;
    }
   *recipe_Ingredient_end = '\0'; 
    
    const char s[2] = "\"";
    char *token;

    /* get the first token */
    token = strtok(recipe_Ingredient, s);
    int token_size = strlen(token);
    ingredients_list_size += token_size;
    ingredients_list =  realloc(ingredients_list,ingredients_list_size);     
    ingredients_list[0] = '\0';
   
    /* walk through other tokens */
    while( token != NULL ) {
      ingredients_list_size += strlen(token) + 2;
      ingredients_list =  realloc(ingredients_list,ingredients_list_size);     

      if (!strcmp(token,","))
        strcat(ingredients_list,"\n");
      else
      strcat(ingredients_list, token);

      token = strtok(NULL, s);
    }
  }
  
  strcat(ingredients_list,"\n");
  return ingredients_list;
}


char * find_Title(char * response)
{ 
  char string_to_search_for[] =  "<title>";
  int size = strlen(string_to_search_for);
  char * recipe_Ingredient = strstr(response,string_to_search_for);
  char * recipe_Ingredient_end = recipe_Ingredient;
  char *ingredients_list = malloc(1);
  int ingredients_list_size = 0;

  if (recipe_Ingredient != NULL){
    printf("Found it!\n");
    recipe_Ingredient += size + 3;
    while (1)
    {
      recipe_Ingredient_end++;
      if(*recipe_Ingredient_end == ']')
        break;
    }
   *recipe_Ingredient_end = '\0'; 
    
    const char s[2] = "\"";
    char *token;
        
    /* get the first token */
    token = strtok(recipe_Ingredient, s);
    int token_size = strlen(token);
    ingredients_list_size += token_size;
    ingredients_list =  realloc(ingredients_list,ingredients_list_size);     
    ingredients_list[0] = '\0';
   
    /* walk through other tokens */
    while( token != NULL ) {
      ingredients_list_size += strlen(token) + 2;
      ingredients_list =  realloc(ingredients_list,ingredients_list_size);     
      
      strcat(ingredients_list, token);
      if (strcmp(token,","))
        strcat(ingredients_list,"\n");         
      token = strtok(NULL, s);
    }
  }
  return ingredients_list;
}