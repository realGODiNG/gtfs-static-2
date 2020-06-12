<template>
    <div id="simple-map">
        Ooops! I should be a map!
    </div>
</template>

<script>
    export default {
        name: 'SimpleMap',

        props: {
            'root': Object
        }
    };
</script>

<style scoped>
    #simple-map {
        background-color: white;
        border: 2px solid #888;
        display: block;
        height: 333px;
        width: 333px;
        text-align: center;
    }
</style>
