var app = angular.module('myApp', ['directive.contextMenu']);

app.controller('Ctrl', function($scope) {
  $scope.clicked = '';
  
  $scope.edit = function() {
    $scope.clicked = 'edit was clicked';
    console.log($scope.clicked);
  };
  
  $scope.properties = function() {
    $scope.clicked = 'properties was clicked';
    console.log($scope.clicked);
  };
  
  $scope.link = function() {
    $scope.clicked = 'link was clicked';
    console.log($scope.clicked);
  };
  
  $scope.delete = function() {
    $scope.clicked = 'delete was clicked';
    console.log($scope.clicked);
  };
});
